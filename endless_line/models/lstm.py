import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from scikeras.wrappers import KerasRegressor
import matplotlib.pyplot as plt
import sklearn
import scikeras

def train_and_save_model(data, model_save_path="lstm_model.pkl"):
    # Preprocess data
    data.clean_data()
    data.data_preprocessing()
    data.merge()

    # Mapping for ENTITY_DESCRIPTION_SHORT
    entity_mapping = {
        'Rapids Ride': 1, 'Oz Theatre': 2, 'Spiral Slide': 3, 'Himalaya Ride': 4, 'Free Fall': 5,
        'Water Ride': 6, 'Merry Go Round': 7, 'Spinning Coaster': 8, 'Go-Karts': 9, 'Bumper Cars': 10,
        'Kiddie Coaster': 11, 'Bungee Jump': 12, 'Roller Coaster': 13, 'Flying Coaster': 14,
        'Haunted House': 15, 'Giga Coaster': 16, 'Crazy Dance': 17, 'Inverted Coaster': 18,
        'Drop Tower': 19, 'Circus Train': 20, 'Zipline': 21, 'Giant Wheel': 22, 'Swing Ride': 23,
        'Dizzy Dropper': 24, 'Superman Ride': 25
    }

    data.merged["ENTITY_DESCRIPTION_SHORT"] = data.merged["ENTITY_DESCRIPTION_SHORT"].map(entity_mapping)

    # Scale features
    columns_to_scale = [
        'NB_UNITS', 'GUEST_CARRIED', 'CAPACITY', 'ADJUST_CAPACITY','UP_TIME', 'DOWNTIME', 
        'NB_MAX_UNIT', 'Num_parade', 'temp', 'feels_like', 'pressure', 'wind_speed', 'clouds_all', 'attendance'
    ]

    scaler = MinMaxScaler()
    data.merged[columns_to_scale] = scaler.fit_transform(data.merged[columns_to_scale])

    data.merged['DEB_TIME'] = pd.to_datetime(data.merged['DEB_TIME'])
    data.merged = data.merged.sort_values('DEB_TIME').set_index('DEB_TIME')
    data.merged = data.merged.dropna()

    target = 'WAIT_TIME_MAX'
    X = data.merged.drop(columns=["WAIT_TIME_MAX"])
    y = data.merged[target]

    # Train/test split
    train_start_date = "2020-06-01"
    train_end_date = "2021-11-30"
    train_data = data.merged[(data.merged["WORK_DATE"] >= train_start_date) & (data.merged["WORK_DATE"] <= train_end_date)]
    target = "WAIT_TIME_MAX"
    non_numeric_columns = ["WORK_DATE"]

    X_train = train_data.drop(columns=[target] + non_numeric_columns).values
    y_train = train_data[target].values

    timesteps = 1
    X_train_reshaped = X_train.reshape(X_train.shape[0], timesteps, X_train.shape[1])

    # Define and train the model
    model = Sequential([
        LSTM(64, input_shape=(X_train_reshaped.shape[1], X_train_reshaped.shape[2]), return_sequences=True),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    model.fit(X_train_reshaped, y_train, epochs=50, batch_size=32)

    # Save the model
    with open(model_save_path, 'wb') as f:
        pickle.dump(model, f)
    print("Model saved to", model_save_path)
    
    return model
