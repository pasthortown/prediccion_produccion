from data_getter import obtener_todos_resultados, obtener_recetas
from model import LSTMCategoryPredictor
import pymongo
from datetime import datetime, timedelta
import pandas as pd
import os
import time

mongo_bdd = os.getenv('mongo_bdd')
mongo_bdd_server = os.getenv('mongo_bdd_server')
mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')

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

def realizar_prediccion():
    if existe_prediccion_hoy():
        print("Ya existen predicciones para la fecha de hoy.")
        return
    df_resultados = obtener_todos_resultados(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password)
    df_recetas = obtener_recetas(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password)
    
    # Normalizar el texto en 'Descripcion_SubRecet' para las claves del diccionario
    df_recetas['Descripcion_SubRecet'] = df_recetas['Descripcion_SubRecet'].apply(normalizar_texto)
    
    # Convertir df_recetas en un diccionario con 'Descripcion_SubRecet' normalizado como índice
    df_recetas = df_recetas.drop_duplicates(subset='Descripcion_SubRecet', keep='first')
    recetas_dict = df_recetas.set_index('Descripcion_SubRecet').to_dict(orient='index')

    predictor = LSTMCategoryPredictor()
    plu_targets = df_resultados['plu_target'].unique()

    for plu_target in plu_targets:
        plu_target_normalizado = normalizar_texto(plu_target)
        plu_target_filename = plu_target_normalizado.replace(" ", "_").strip()
        fecha_hoy = datetime.utcnow().strftime('%Y%m%d')
        model_filename = f"models/model_{plu_target_filename}_{fecha_hoy}.h5"
        scaler_filename = f"models/scaler_{plu_target_filename}_{fecha_hoy}.pkl"
        
        if not os.path.exists(model_filename) or not os.path.exists(scaler_filename):
            print(f"Modelo o scaler para {plu_target} no encontrado. Iniciando entrenamiento...")
            df_filtrado = df_resultados[df_resultados['plu_target'] == plu_target]
            X, y, _ = predictor.load_and_prepare_data(df_filtrado)
            predictor.train_model(X, y, 20, 1)
            predictor.save_model(model_filename, scaler_filename)
            print(f"Modelo y scaler para {plu_target} entrenados y guardados.")
        else:
            print(f"Modelo y scaler para {plu_target} encontrados. Cargando...")

    predicciones = []
    now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=50)
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
            plu_target_filename = plu_target_normalizado.replace(" ", "_").strip()
            fecha_hoy = datetime.utcnow().strftime('%Y%m%d')
            model_filename = f"models/model_{plu_target_filename}_{fecha_hoy}.h5"
            scaler_filename = f"models/scaler_{plu_target_filename}_{fecha_hoy}.pkl"
            
            predictor.load_model(model_filename, scaler_filename)
            current_df = pd.DataFrame([current_params])
            scaled_current_data = predictor.scaler.transform(current_df[['dia_semana', 'mes', 'dia_mes', 'hora', 'minuto']])
            scaled_current_data = scaled_current_data.reshape((scaled_current_data.shape[0], 1, scaled_current_data.shape[1]))
            
            predicted = predictor.model.predict(scaled_current_data)
            
            # Obtener los datos de la receta para el plu_target actual
            receta_info = recetas_dict.get(plu_target_normalizado, {})
            peso_unitario = receta_info.get('Cantidad', 0)
            unidad = receta_info.get('Unidad_Receta', '')

            cuenta_prediccion = float(predicted[0][0])
            peso_prediccion = peso_unitario * cuenta_prediccion

            prediccion_intervalo.append({
                'plu_target': plu_target,
                'cuenta_prediccion': cuenta_prediccion,
                'peso_unitario': peso_unitario,
                'peso_prediccion': peso_prediccion,
                'unidad': unidad
            })
        predicciones.append({
            'hora_desde': hora_desde,
            'hora_hasta': hora_hasta,
            'prediccion': prediccion_intervalo
        })
        
        now += timedelta(minutes=10)
    guardar_predicciones(predicciones)

while(True):
    realizar_prediccion()
    time.sleep(60)
