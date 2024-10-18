import pyodbc
from datetime import timedelta
import os
from maxpoint_credentials import get_maxpoint_credentials
import pymongo
from datetime import datetime

mongo_bdd = os.getenv('mongo_bdd')
mongo_bdd_server = os.getenv('mongo_bdd_server')
mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
intervalo_minutos = int(os.getenv('intervalo_minutos'))

server, database, username, password = get_maxpoint_credentials()

conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def round_time_to_nearest_interval(time, interval_minutes):
    remainder = time.minute % interval_minutes
    if remainder < interval_minutes / 2:
        return time - timedelta(minutes=remainder, seconds=time.second, microseconds=time.microsecond)
    else:
        return time + timedelta(minutes=interval_minutes - remainder, seconds=-time.second, microseconds=-time.microsecond)

def get_fecha_minima_from_db(cursor):
    database_uri = 'mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_bdd_server + '/'
    client = pymongo.MongoClient(database_uri)
    db = client[mongo_bdd]
    sales_data_collection = db['sales_data']
    result = sales_data_collection.find_one(
        {}, 
        sort=[("fecha_fin", -1)],
        projection={"fecha_fin": 1}
    )
    fecha_minima_permitida = datetime(2024, 1, 1, 7, 0)
    if result and result.get("fecha_fin"):
        fecha_minima_resultados = result["fecha_fin"]
        return fecha_minima_resultados
    cursor.execute("SELECT MIN(Cabecera_Factura.cfac_fechacreacion) FROM Cabecera_Factura")
    fecha_minima_cabecera = cursor.fetchone()[0]
    if fecha_minima_cabecera:
        if fecha_minima_cabecera < fecha_minima_permitida:
            return fecha_minima_permitida
        return fecha_minima_cabecera.replace(hour=7, minute=0, second=0, microsecond=0)
    
def get_fecha_maxima_from_db(cursor):
    cursor.execute("SELECT MAX(Cabecera_Factura.cfac_fechacreacion) FROM Cabecera_Factura")
    fecha_maxima = cursor.fetchone()[0]
    if fecha_maxima:
        return round_time_to_nearest_interval(fecha_maxima, intervalo_minutos)
    else:
        raise Exception("No se pudo obtener la fecha máxima de Cabecera_Factura.")

def build_maxpoint_sales_data():
    database_uri = 'mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_bdd_server + '/'
    client = pymongo.MongoClient(database_uri)
    db = client[mongo_bdd]
    recetas_collection = db['recetas']
    sales_data_collection = db['sales_data']
    cod_plu_list = [receta["Cod_Plu"] for receta in recetas_collection.find({}, {"Cod_Plu": 1})]
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    fecha_minima = get_fecha_minima_from_db(cursor)
    fecha_actual_redondeada = get_fecha_maxima_from_db(cursor)
    with open('get_data_sales.sql', 'r') as file:
        sql_script_template = file.read()
    while fecha_minima < fecha_actual_redondeada:
        fecha_maxima = fecha_minima + timedelta(minutes=intervalo_minutos)
        if fecha_maxima > fecha_actual_redondeada:
            fecha_maxima = fecha_actual_redondeada
        try:
            cursor.execute(sql_script_template, fecha_minima, fecha_maxima, intervalo_minutos)
            rows = cursor.fetchall()
            sales_data_documents = []
            for row in rows:
                if row.plu_num_plu in cod_plu_list:
                    sales_data_documents.append({
                        "plu_num_plu": row.plu_num_plu,
                        "Cuenta": row.Cuenta,
                        "fecha_inicio": row.fecha_inicio,
                        "fecha_fin": row.fecha_fin
                    })
            if sales_data_documents:
                sales_data_collection.insert_many(sales_data_documents)
        except Exception as e:
            print(f"Error al ejecutar el script para el intervalo {fecha_minima} - {fecha_maxima}: {e}")
        fecha_minima = fecha_maxima
    cursor.close()
    conn.close()
    client.close()