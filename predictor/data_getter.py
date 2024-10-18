import os
import pandas as pd
import pymongo
import numpy as np

def obtener_recetas(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password):
    database_uri = 'mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_bdd_server + '/'
    client = pymongo.MongoClient(database_uri)
    db = client[mongo_bdd]
    collection = db['recetas']
    recetas = collection.find()
    df = pd.DataFrame(list(recetas))
    return df

def obtener_ventas(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password):
    database_uri = 'mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_bdd_server + '/'
    client = pymongo.MongoClient(database_uri)
    db = client[mongo_bdd]
    collection = db['sales_data']
    sales_data = collection.find()
    df = pd.DataFrame(list(sales_data))
    return df



def obtener_todos_resultados(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password):
    recetas = obtener_recetas(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password)
    ventas = obtener_ventas(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password)
    recetas_dict = recetas.drop_duplicates(subset='Cod_Plu').set_index('Cod_Plu').to_dict(orient='index')
    plu_targets_unicos = recetas['Descripcion_SubRecet'].unique()
    resultados_completos = []
    
    # Convertir las fechas a formato datetime
    ventas['fecha_inicio'] = pd.to_datetime(ventas['fecha_inicio'])
    ventas['fecha_fin'] = pd.to_datetime(ventas['fecha_fin'])
    
    # Obtener periodos únicos de tiempo
    periodos_tiempo = ventas[['fecha_inicio', 'fecha_fin']].drop_duplicates().sort_values(by='fecha_inicio')
    
    for _, periodo in periodos_tiempo.iterrows():
        fecha_inicio = periodo['fecha_inicio']
        fecha_fin = periodo['fecha_fin']
        
        # Filtrar ventas en el periodo actual
        ventas_en_periodo = ventas[(ventas['fecha_inicio'] == fecha_inicio) & (ventas['fecha_fin'] == fecha_fin)]
        
        # Agrupar por plu_num_plu y sumar la cantidad en caso de duplicados
        ventas_agrupadas = ventas_en_periodo.groupby('plu_num_plu', as_index=False).agg({'Cuenta': 'sum'})
        
        for plu_target in plu_targets_unicos:
            venta = ventas_agrupadas[ventas_agrupadas['plu_num_plu'] == plu_target]
            
            if venta.empty:
                receta_info = recetas_dict.get(plu_target)
                if receta_info:
                    venta_completa = {
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "plu_num_plu": plu_target,
                        "plu_name": receta_info.get('Descripcion_Plu', ''),
                        "plu_target": receta_info.get('Descripcion_SubRecet', ''),
                        "Cuenta": 0,
                        "Unidad_Receta": receta_info.get('Unidad_Receta', '')
                    }
                else:
                    venta_completa = {
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "plu_num_plu": plu_target,
                        "plu_name": '',
                        "plu_target": plu_target,
                        "Cuenta": 0,
                        "Unidad_Receta": ''
                    }
            else:
                venta_completa = venta.iloc[0].to_dict()
                receta_info = recetas_dict.get(venta_completa['plu_num_plu'])
                if receta_info:
                    venta_completa.update({
                        "plu_name": receta_info.get('Descripcion_Plu', ''),
                        "plu_target": receta_info.get('Descripcion_SubRecet', ''),
                        "Cuenta": venta_completa.get('Cuenta', ''),
                        "Unidad_Receta": receta_info.get('Unidad_Receta', '')
                    })

            resultados_completos.append(venta_completa)
    
    df = pd.DataFrame(resultados_completos)

    # Agregar las columnas adicionales
    df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'])
    df['dia_semana'] = df['fecha_inicio'].dt.dayofweek
    df['mes'] = df['fecha_inicio'].dt.month
    df['dia_mes'] = df['fecha_inicio'].dt.day
    df['hora'] = df['fecha_inicio'].dt.hour
    df['minuto'] = df['fecha_inicio'].dt.minute

    return df
