import numpy as np
from model import crear_modelo_lstm, preparar_datos_para_modelo

def predecir_para_fecha(df, subreceta, dia_mes, dia_semana, mes, hora, minuto):
    # Preparar los datos para el modelo y obtener el scaler
    X, y, scaler = preparar_datos_para_modelo(df, subreceta)
    
    # Crear el modelo LSTM y entrenar con los datos históricos
    modelo = crear_modelo_lstm((X.shape[1], 1))
    modelo.fit(X, y, batch_size=1, epochs=1)  # Ajusta las épocas según tus necesidades
    
    # Crear los datos de entrada personalizados para la predicción
    entrada_personalizada = np.array([[dia_semana, mes, dia_mes, hora, minuto]])
    
    # Normalizar los datos de entrada personalizados
    entrada_normalizada = scaler.transform(entrada_personalizada)
    
    # Redimensionar para que sea compatible con el LSTM
    entrada_normalizada = np.reshape(entrada_normalizada, (entrada_normalizada.shape[0], entrada_normalizada.shape[1], 1))
    
    # Hacer la predicción
    prediccion = modelo.predict(entrada_normalizada)
    
    # Desnormalizar la predicción (sólo la cantidad)
    prediccion_desnormalizada = scaler.inverse_transform(np.array([[0, 0, 0, 0, prediccion[0][0]]]))[0][4]
    
    return prediccion_desnormalizada
