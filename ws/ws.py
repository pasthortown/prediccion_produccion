import tornado.ioloop
import tornado.web
import json
import os
from pymongo import MongoClient

mongo_bdd = os.getenv('mongo_bdd')
mongo_bdd_server = os.getenv('mongo_bdd_server')
mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')

database_uri = 'mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_bdd_server + '/'
client = MongoClient(database_uri)
db = client[mongo_bdd]

class PrediccionHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*") 
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.set_header("Access-Control-Allow-Credentials", "true")


    def options(self, anio, mes, dia):
        self.set_status(204)
        self.set_header("Access-Control-Allow-Origin", "*") 
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.finish()

    def get(self, anio, mes, dia):
        fecha_parametro = f"{anio}/{mes}/{dia}"
        prediccion = db['predicciones'].find_one({'date': fecha_parametro})

        if prediccion:
            prediccion['_id'] = str(prediccion['_id'])
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(prediccion, indent=4))
        else:
            self.set_status(404)
            self.write(json.dumps({'error': f'No prediction found for {fecha_parametro}'}, indent=4))

def make_app():
    return tornado.web.Application([
        (r"/prediccion/([0-9]{4})/([0-9]{2})/([0-9]{2})", PrediccionHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(address='0.0.0.0', port=5055)
    tornado.ioloop.IOLoop.current().start()
