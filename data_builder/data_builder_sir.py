import pyodbc
import os
import pymongo
from datetime import datetime

sir_server = os.getenv('sir_server')
sir_database = os.getenv('sir_database')
sir_username = os.getenv('sir_username')
sir_password = os.getenv('sir_password')
mongo_bdd = os.getenv('mongo_bdd')
mongo_bdd_server = os.getenv('mongo_bdd_server')
mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')

sir_conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={sir_server};DATABASE={sir_database};UID={sir_username};PWD={sir_password}'

def get_data_recetas():
    sir_conn = pyodbc.connect(sir_conn_str)
    sir_cursor = sir_conn.cursor()
    with open('get_data_recetas.sql', 'r') as file:
        sql_script = file.read()
    sir_cursor.execute(sql_script)
    data = sir_cursor.fetchall()
    sir_cursor.close()
    sir_conn.close()
    return data

def clear_collection_recetas():
    database_uri = 'mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_bdd_server + '/'
    client = pymongo.MongoClient(database_uri)
    db = client[mongo_bdd]
    collection = db['recetas']
    collection.delete_many({})
    client.close()

def insert_into_recetas(data):
    database_uri = 'mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_bdd_server + '/'
    client = pymongo.MongoClient(database_uri)
    db = client[mongo_bdd]
    collection = db['recetas']
    recetas_to_insert = []
    timestamp = datetime.now()
    for row in data:
        receta = {
            "Cod_Plu": row.Cod_Plu,
            "Descripcion_Plu": row.Descripcion_Plu,
            "Descripcion_SubRecet": row.Descripcion_SubRecet,
            "Cantidad": row.Cantidad,
            "Unidad_Receta": row.Unidad_Receta,
            "timestamp": timestamp
        }
        recetas_to_insert.append(receta)
    if recetas_to_insert:
        collection.insert_many(recetas_to_insert)
    client.close()

def update_data_recetas():
    database_uri = f'mongodb://{mongo_user}:{mongo_password}@{mongo_bdd_server}/'
    try:
        client = pymongo.MongoClient(database_uri, serverSelectionTimeoutMS=20000)
        db = client[mongo_bdd]
        collection = db['recetas']
        last_document = collection.find_one(
            {}, 
            sort=[("timestamp", -1)]
        )
        is_collection_empty = last_document is None
        client.close()
        now = datetime.now()
        today_date = now.date()
        if is_collection_empty or last_document["timestamp"].date() != today_date:
            clear_collection_recetas()
            data = get_data_recetas()
            insert_into_recetas(data)
        else:
            print("La colección 'recetas' ya está actualizada con la fecha de hoy.")
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(f"Error de conexión con MongoDB: {e}")
    except Exception as e:
        print(f"Ocurrió un error al actualizar la colección 'recetas': {e}")