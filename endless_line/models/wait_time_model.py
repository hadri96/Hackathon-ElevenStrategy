import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn import preprocessing
import matplotlib
from matplotlib import pyplot as plt
import os

from endless_line.models.model_utils import save_model, load_model
from endless_line.data_utils.dashboard_utils import DataLoader

class Forecaster():
    def __init__(self, filename='wait_time_predictor.pkl', csv_name='waiting_time_predicted.csv'):
        self.filename = filename
        self.csv_name = csv_name
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # XGBoost parameters (auto-detects CPU/GPU)
        self.params = {
            "objective": "reg:squarederror",
            "eval_metric": "rmse",
            "eta": 0.1,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "n_jobs": -1,  # Use all CPU cores
            "device": device
        }

        # based on average waiting time of the attraction on the whole dataset
        self.attraction_encoding = {
            'Spiral Slide': 0,
            'Giant Wheel': 1,
            'Swing Ride': 2,
            'Free Fall': 3,
            'Go-Karts': 4,
            'Zipline': 5,
            'Spinning Coaster': 6,
            'Drop Tower': 7,
            'Water Ride': 8,
            'Bungee Jump': 9,
            'Flying Coaster': 10,
            'Roller Coaster': 11,
            'Haunted House': 12,
            'Rapids Ride': 13,
            'Inverted Coaster': 14,
            'Superman Ride': 15,
            'Dizzy Dropper': 16,
            'Bumper Cars': 17,
            'Giga Coaster': 18,
            'Merry Go Round': 19,
            'Kiddie Coaster': 20,
            'Circus Train': 21,
            'Crazy Dance': 22,
            'Oz Theatre': 23,
            'Himalaya Ride': 24
        }
        # decoding dict of the previous encoding dict
        self.attraction_decoding = {
            0: 'Spiral Slide',
            1: 'Giant Wheel',
            2: 'Swing Ride',
            3: 'Free Fall',
            4: 'Go-Karts',
            5: 'Zipline',
            6: 'Spinning Coaster',
            7: 'Drop Tower',
            8: 'Water Ride',
            9: 'Bungee Jump',
            10: 'Flying Coaster',
            11: 'Roller Coaster',
            12: 'Haunted House',
            13: 'Rapids Ride',
            14: 'Inverted Coaster',
            15: 'Superman Ride',
            16: 'Dizzy Dropper',
            17: 'Bumper Cars',
            18: 'Giga Coaster',
            19: 'Merry Go Round',
            20: 'Kiddie Coaster',
            21: 'Circus Train',
            22: 'Crazy Dance',
            23: 'Oz Theatre',
            24: 'Himalaya Ride'
        }

    def featuring(self, df, train=True):
        """
            final featuring specific to this model
        """
        # make sure datetimes are of the right type
        df["DEB_TIME"] = df["DEB_TIME"].astype('datetime64[ns]')
        df['WORK_DATE'] = df['WORK_DATE'].astype('datetime64[ns]')

        # create new features
        df["year"] = df["WORK_DATE"].dt.year
        df["minute"] = df["DEB_TIME"].dt.minute

        # Select columns to scale
        columns_to_scale = ['GUEST_CARRIED', 'CAPACITY', 'ADJUST_CAPACITY', 'NB_UNITS', 'NB_MAX_UNIT', 'OPEN_TIME', 'UP_TIME', 'DOWNTIME', 'hour', 'day', 'month', 'year', 'minute']

        if train:
            self.scaler = MinMaxScaler()
            # Apply MinMaxScaler to selected columns
            df[columns_to_scale] = self.scaler.fit_transform(df[columns_to_scale])
        else:
            # Apply MinMaxScaler to selected columns
            df[columns_to_scale] = self.scaler.transform(df[columns_to_scale])

        # drop unnecessary columns
        df = df.drop(columns=['FIN_TIME', 'DEB_TIME_HOUR'])

        # label encoding of attraction names (ordered by average waiting time)
        df['attraction_encoded']= df['ENTITY_DESCRIPTION_SHORT'].apply(lambda x: self.attraction_encoding[x])
        df = df.drop(columns='ENTITY_DESCRIPTION_SHORT')

        if train:
            # we need those columns for the prediction 
            df = df.drop(columns=['WORK_DATE', 'DEB_TIME'])

        return df

    def fit(self, df_train):

        df_train_y = df_train[['WAIT_TIME_MAX']]
        df_train_x = df_train.drop(columns=['WAIT_TIME_MAX'])

        # Final featuring
        df_train_x = self.featuring(df_train_x)
        
        # Convert to DMatrix (optional, but improves efficiency)
        dtrain = xgb.DMatrix(df_train_x, label=df_train_y)
        #dval = xgb.DMatrix(df_val_x, label=df_val_y)

        evals = [(dtrain, "train")]#, (dval, "val")]
        
        # train model
        self.model = xgb.train(self.params, dtrain, num_boost_round=1000, evals=evals, early_stopping_rounds=10)
        #save_model(self.model, self.filename)

    def predict(self, X, pivot=True, export=True):
        """
            need X to have DEB_TIME and WORK_DATE
        """
        # Final featuring
        X = self.featuring(X, train=False)

        # create the input matrix of the model
        X_pred = X.drop(columns=['WORK_DATE', 'DEB_TIME'])
        X_pred = xgb.DMatrix(X_pred)

        # Load the saved model
        model = self.model  #model = load_model(self.filename)

        # predict and merge predictions with X
        y_pred = model.predict(X_pred)
        res = X.copy()
        res['PRED'] = y_pred

        # only keep necessary columns for plotting
        res = res[['WORK_DATE', 'DEB_TIME', 'PRED', 'attraction_encoded']]

        # pivot the tables
        if pivot:
            res = self.pivot(res)

        # export it as csv 
        if export:
            self.export(res, self.csv_name)

        return res
    
    def pivot(self,df):
        df['attraction'] = df['attraction_encoded'].apply(lambda x: self.attraction_decoding[x])
        df = df.drop(columns=['attraction_encoded'])
        df_pivot = df.pivot(index='DEB_TIME', columns='attraction', values='PRED')
        return df_pivot
    
    def export(self, df, csv_name):
        root_dir = DataLoader().root_dir
        os.path.join(root_dir,csv_name)
        df.to_csv(csv_name)
