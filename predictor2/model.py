import numpy as np
import os
import json
import pickle
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import pandas as pd

class LSTMCategoryPredictor:
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        self.model_dir = "models"
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    def preparar_datos_para_modelo(self, df, subreceta):
        df_filtrado = df[df['Descripcion_SubRecet'] == subreceta].copy()
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        df_filtrado[['dia_semana', 'mes', 'dia_mes', 'hora', 'minuto']] = self.scaler.fit_transform(
            df_filtrado[['dia_semana', 'mes', 'dia_mes', 'hora', 'minuto']]
        )
        X = df_filtrado[['dia_semana', 'mes', 'dia_mes', 'hora', 'minuto']].values
        y = df_filtrado['Cantidad'].values
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        return X, y

    def crear_modelo_lstm(self, input_shape):
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train_and_save_model(self, df, subreceta, epochs=1, batch_size=1):
        X, y = self.preparar_datos_para_modelo(df, subreceta)
        self.model = self.crear_modelo_lstm((X.shape[1], 1))
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
        plu_target_filename = subreceta.strip().lower().replace(" ", "_")
        date_str = datetime.utcnow().strftime('%Y%m%d')
        model_filename = os.path.join(self.model_dir, f"model_{plu_target_filename}_{date_str}.h5")
        scaler_filename = os.path.join(self.model_dir, f"scaler_{plu_target_filename}_{date_str}.pkl")
        self.save_model(model_filename, scaler_filename)

    def save_model(self, model_filename: str, scaler_filename: str) -> None:
        self.model.save(model_filename)
        with open(scaler_filename, 'wb') as f:
            pickle.dump(self.scaler, f)

    def load_model(self, model_filename: str, scaler_filename: str) -> None:
        self.model = load_model(model_filename)
        with open(scaler_filename, 'rb') as f:
            self.scaler = pickle.load(f)

    def predecir_para_fecha(self, dia_semana, mes, dia_mes, hora, minuto, subreceta):
        plu_target_filename = subreceta.strip().lower().replace(" ", "_")
        date_str = datetime.utcnow().strftime('%Y%m%d')
        model_filename = os.path.join(self.model_dir, f"model_{plu_target_filename}_{date_str}.h5")
        scaler_filename = os.path.join(self.model_dir, f"scaler_{plu_target_filename}_{date_str}.pkl")

        if os.path.exists(model_filename) and os.path.exists(scaler_filename):
            self.load_model(model_filename, scaler_filename)
            entrada_personalizada = np.array([[dia_semana, mes, dia_mes, hora, minuto]])
            entrada_normalizada = self.scaler.transform(entrada_personalizada)
            entrada_normalizada = np.reshape(entrada_normalizada, (entrada_normalizada.shape[0], entrada_normalizada.shape[1], 1))
            prediccion = self.model.predict(entrada_normalizada)
            prediccion_desnormalizada = self.scaler.inverse_transform(np.array([[0, 0, 0, 0, prediccion[0][0]]]))[0][4]
            return prediccion_desnormalizada
        else:
            print(f"Modelo o scaler para {subreceta} no encontrado.")
            return None

    def predict(self, df: pd.DataFrame) -> str:
        predicciones = []
        for _, row in df.iterrows():
            plu_target = row['Descripcion_SubRecet'].lower().replace(" ", "_").strip()
            prediccion = self.predecir_para_fecha(
                dia_semana=row['dia_semana'],
                mes=row['mes'],
                dia_mes=row['dia_mes'],
                hora=row['hora'],
                minuto=row['minuto'],
                subreceta=plu_target
            )
            if prediccion is not None:
                predicciones.append({'Descripcion_SubRecet': row['Descripcion_SubRecet'], 'cantidad': float(prediccion)})
        resultado_json = json.dumps({'predicciones': predicciones}, indent=4)
        return resultado_json
