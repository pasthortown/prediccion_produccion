import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
import pickle
import json
import os
from typing import Tuple
from datetime import datetime

class LSTMCategoryPredictor:
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()

    def load_and_prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, pd.Series]:
        try:
            # Añadir 'plu_target' a los datos
            feature_columns = ['dia_semana', 'mes', 'dia_mes', 'hora', 'minuto']
            X = data[feature_columns].values
            y = data['Cuenta'].values
            plu_target = data['plu_target']  # Obtener plu_target para luego asignar predicciones
            scaled_X = self.scaler.fit_transform(X)
            X_scaled, y_scaled = self.create_sequences(scaled_X, y)
            return X_scaled, y_scaled, plu_target
        except Exception as e:
            raise

    def create_sequences(self, X: np.ndarray, y: np.ndarray, time_step: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        X_seq, y_seq = [], []
        for i in range(len(X) - time_step):
            X_seq.append(X[i:(i + time_step)])
            y_seq.append(y[i + time_step])  # Asegúrate de que y siga a X correctamente
        return np.array(X_seq), np.array(y_seq)

    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        try:
            model = Sequential()
            model.add(LSTM(50, activation='relu', input_shape=input_shape))
            model.add(Dropout(0.2))
            model.add(Dense(input_shape[1]))
            model.compile(optimizer='adam', loss='mse')
            return model
        except Exception as e:
            raise

    def train_model(self, X_train: np.ndarray, y_train: np.ndarray, epochs: int = 50, batch_size: int = 1) -> None:
        try:
            self.model = self.build_model((X_train.shape[1], X_train.shape[2]))
            early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.2, patience=5, min_lr=1e-5)
            self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1, callbacks=[early_stopping, reduce_lr])
        except Exception as e:
            raise

    def predict(self, df: pd.DataFrame) -> str:
        try:
            predicciones = []
            for _, row in df.iterrows():
                plu_target = row['plu_target'].lower().replace(" ", "_").strip()  # Formato del plu_target
                model_filename = f"model_{plu_target}_{datetime.utcnow().strftime('%Y%m%d')}.h5"
                scaler_filename = f"scaler_{plu_target}.pkl"

                if os.path.exists(model_filename) and os.path.exists(scaler_filename):
                    self.load_model(model_filename, scaler_filename)

                    current_params = {
                        'dia_semana': row['dia_semana'],
                        'mes': row['mes'],
                        'dia_mes': row['dia_mes'],
                        'hora': row['hora'],
                        'minuto': row['minuto']
                    }
                    current_df = pd.DataFrame([current_params])
                    scaled_current_data = self.scaler.transform(current_df[['dia_semana', 'mes', 'dia_mes', 'hora', 'minuto']])
                    scaled_current_data = scaled_current_data.reshape((scaled_current_data.shape[0], 1, scaled_current_data.shape[1]))
                    predicted = self.model.predict(scaled_current_data)
                    predicciones.append({'plu_target': row['plu_target'], 'cantidad': float(predicted[0][0])})
                else:
                    print(f"Modelo para {plu_target} no encontrado.")
                    
            resultado_json = json.dumps({'predicciones': predicciones}, indent=4)
            return resultado_json
        except Exception as e:
            raise

    def save_model(self, model_filename: str, scaler_filename: str) -> None:
        try:
            self.model.save(model_filename)
            with open(scaler_filename, 'wb') as f:
                pickle.dump(self.scaler, f)
        except Exception as e:
            raise

    def load_model(self, model_filename: str, scaler_filename: str) -> None:
        try:
            self.model = load_model(model_filename)
            with open(scaler_filename, 'rb') as f:
                self.scaler = pickle.load(f)
        except Exception as e:
            raise

    def train_and_save_for_each_plu(self, data: pd.DataFrame) -> None:
        plu_targets = data['plu_target'].unique()
        for plu_target in plu_targets:
            print(f"Entrenando modelo para {plu_target}")
            data_filtered = data[data['plu_target'] == plu_target]
            X, y, _ = self.load_and_prepare_data(data_filtered)

            # Entrenar modelo
            self.train_model(X, y, 5, 1)

            # Guardar el modelo y el scaler
            plu_target_filename = plu_target.lower().replace(" ", "_").strip()
            model_filename = f"model_{plu_target_filename}_{datetime.utcnow().strftime('%Y%m%d')}.h5"
            scaler_filename = f"scaler_{plu_target_filename}.pkl"
            self.save_model(model_filename, scaler_filename)
            print(f"Modelo para {plu_target} guardado.")
