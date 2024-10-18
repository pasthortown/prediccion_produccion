import os
import glob
import pymongo
import pandas as pd
from datetime import datetime, timedelta
from data_getter import obtener_todos_resultados, obtener_recetas
from model import LSTMCategoryPredictor
import time

mongo_bdd = 'prediction'
mongo_bdd_server = 'localhost'
mongo_user = 'mongo'
mongo_password = '12345678'

def get_mongo_client():
    database_uri = f'mongodb://{mongo_user}:{mongo_password}@{mongo_bdd_server}/'
    client = pymongo.MongoClient(database_uri)
    return client

def existe_prediccion_hoy():
    client = get_mongo_client()
    db = client[mongo_bdd]
    collection = db['predicciones']
    hoy = datetime.utcnow().strftime('%Y/%m/%d')
    return collection.find_one({'date': hoy}) is not None

def guardar_predicciones(predicciones):
    client = get_mongo_client()
    db = client[mongo_bdd]
    collection = db['predicciones']
    hoy = datetime.utcnow().strftime('%Y/%m/%d')
    prediccion_obj = {
        'date': hoy,
        'predicciones': predicciones
    }
    collection.insert_one(prediccion_obj)
    print(f"Predicciones guardadas para la fecha: {hoy}")

def normalizar_texto(texto):
    return texto.strip().lower()

def limpiar_modelos_antiguos(model_dir, fecha_actual):
    """Elimina todos los modelos y scalers de fechas diferentes a la actual"""
    archivos_antiguos = glob.glob(os.path.join(model_dir, '*'))
    for archivo in archivos_antiguos:
        if fecha_actual not in archivo:
            os.remove(archivo)
    print("Modelos y scalers antiguos eliminados.")

def existen_modelos_para_hoy(plu_target, model_dir, fecha_actual):
    """Verifica si existen los modelos y scalers de hoy para el plu_target"""
    plu_target_filename = normalizar_texto(plu_target).replace(" ", "_")
    model_filename = os.path.join(model_dir, f"model_{plu_target_filename}_{fecha_actual}.h5")
    scaler_filename = os.path.join(model_dir, f"scaler_{plu_target_filename}_{fecha_actual}.pkl")
    return os.path.exists(model_filename) and os.path.exists(scaler_filename)

def realizar_prediccion():
    if existe_prediccion_hoy():
        print("Ya existen predicciones para la fecha de hoy.")
        return

    # Obtener los datos de resultados y recetas
    df_resultados = obtener_todos_resultados(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password)
    df_recetas = obtener_recetas(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password)

    # Normalizar el texto en 'Descripcion_SubRecet' para las claves del diccionario
    df_recetas['Descripcion_SubRecet'] = df_recetas['Descripcion_SubRecet'].apply(normalizar_texto)
    
    # Convertir df_recetas en un diccionario
    recetas_dict = df_recetas.drop_duplicates(subset='Descripcion_SubRecet').set_index('Descripcion_SubRecet').to_dict(orient='index')

    predictor = LSTMCategoryPredictor()
    plu_targets = df_resultados['Descripcion_SubRecet'].unique()

    # Obtener la fecha actual
    fecha_hoy = datetime.utcnow().strftime('%Y%m%d')
    limpiar_modelos_antiguos(predictor.model_dir, fecha_hoy)

    # Revisar si ya existen modelos y scalers para cada plu_target
    for plu_target in plu_targets:
        if not existen_modelos_para_hoy(plu_target, predictor.model_dir, fecha_hoy):
            print(f"Modelo o scaler para {plu_target} no encontrado. Iniciando entrenamiento...")
            predictor.train_and_save_model(df_resultados, plu_target, epochs=20, batch_size=1)
            print(f"Modelo y scaler para {plu_target} entrenados y guardados.")
        else:
            print(f"Modelo y scaler para {plu_target} ya existen y fueron cargados.")

    predicciones = []
    now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=50)

    # Ahora no entrenamos en cada iteración, sino que solo cargamos el modelo y predecimos
    while now <= end_of_day:
        hora_desde = now.strftime('%H:%M')
        hora_hasta = (now + timedelta(minutes=10)).strftime('%H:%M')
        prediccion_intervalo = []
        current_params = {
            'dia_semana': now.weekday(),
            'mes': now.month,
            'dia_mes': now.day,
            'hora': now.hour,
            'minuto': now.minute
        }

        for plu_target in plu_targets:
            plu_target_normalizado = normalizar_texto(plu_target)
            plu_target_filename = plu_target_normalizado.replace(" ", "_")
            model_filename = os.path.join(predictor.model_dir, f"model_{plu_target_filename}_{fecha_hoy}.h5")
            scaler_filename = os.path.join(predictor.model_dir, f"scaler_{plu_target_filename}_{fecha_hoy}.pkl")
            
            # Cargar modelo y scaler solo una vez y hacer la predicción
            predictor.load_model(model_filename, scaler_filename)
            
            # Crear el DataFrame con los parámetros actuales
            current_df = pd.DataFrame([current_params])
            
            # Normalizar los datos de entrada
            scaled_current_data = predictor.scaler.transform(current_df[['dia_semana', 'mes', 'dia_mes', 'hora', 'minuto']])
            
            # Ajustar la forma de los datos para el modelo LSTM (None, 5, 1)
            scaled_current_data = scaled_current_data.reshape((scaled_current_data.shape[0], scaled_current_data.shape[1], 1))

            # Hacer la predicción
            predicted = predictor.model.predict(scaled_current_data)

            receta_info = recetas_dict.get(plu_target_normalizado, {})
            peso_unitario = receta_info.get('Cantidad', 0)
            unidad = receta_info.get('Unidad_Receta', '')

            cuenta_prediccion = float(predicted[0][0])
            peso_prediccion = peso_unitario * cuenta_prediccion

            prediccion_intervalo.append({
                'plu_target': plu_target.strip(),
                'cuenta_prediccion': cuenta_prediccion,
                'peso_unitario': peso_unitario,
                'peso_prediccion': peso_prediccion,
                'unidad': unidad.strip()
            })

        toAppend = {
            'hora_desde': hora_desde,
            'hora_hasta': hora_hasta,
            'prediccion': prediccion_intervalo
        }
        predicciones.append(toAppend)
        now += timedelta(minutes=10)

    guardar_predicciones(predicciones)


# Bucle principal para ejecutar predicciones cada 60 segundos
while True:
    realizar_prediccion()
    time.sleep(60)
