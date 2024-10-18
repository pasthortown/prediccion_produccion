from data_builder_sir import update_data_recetas
from data_builder_sales import build_maxpoint_sales_data
import time

while True:
    update_data_recetas()
    build_maxpoint_sales_data()
    time.sleep(10)
