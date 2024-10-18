import os
import pandas as pd
import pymongo
import numpy as np

def obtener_recetas(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password):
    database_uri = 'mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_bdd_server + '/'
    client = pymongo.MongoClient(database_uri)
    db = client[mongo_bdd]
    collection = db['recetas']
    recetas = pd.DataFrame(list(collection.find()))
    return recetas

def obtener_ventas(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password):
    database_uri = 'mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_bdd_server + '/'
    client = pymongo.MongoClient(database_uri)
    db = client[mongo_bdd]
    collection = db['sales_data']
    ventas = pd.DataFrame(list(collection.find()))
    return ventas

def convertir_fecha(fecha):
    if isinstance(fecha, dict) and '$date' in fecha:
        return pd.to_datetime(fecha['$date'])
    else:
        return pd.to_datetime(fecha)
    
def obtener_todos_resultados(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password):
    recetas = obtener_recetas(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password)
    ventas = obtener_ventas(mongo_bdd_server, mongo_bdd, mongo_user, mongo_password)
    ventas['fecha_inicio'] = ventas['fecha_inicio'].apply(convertir_fecha)
    ventas['fecha_fin'] = ventas['fecha_fin'].apply(convertir_fecha)
    df = pd.merge(ventas, recetas, left_on='plu_num_plu', right_on='Cod_Plu')
    df['dia_semana'] = df['fecha_inicio'].dt.weekday
    df['mes'] = df['fecha_inicio'].dt.month
    df['dia_mes'] = df['fecha_inicio'].dt.day
    df['hora'] = df['fecha_inicio'].dt.hour
    df['minuto'] = df['fecha_inicio'].dt.minute
    df_agrupado = df.groupby(['dia_semana', 'mes', 'dia_mes', 'hora', 'minuto', 'Descripcion_SubRecet']).agg({
        'Cantidad': 'sum'
    }).reset_index()
    return df_agrupado