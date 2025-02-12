import pandas as pd
import numpy as np
from endless_line.data_utils.dataloader import DataLoader
from endless_line.data_utils.weather_forecast import WeatherForecast
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from prophet import Prophet

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def merge_for_attendance_forecasting(df, df_weather):
    df_weather['dt_iso'] = pd.to_datetime(df_weather['dt_iso'])
    # Merge the dataframes
    merged_df = pd.merge(df, df_weather, left_on='USAGE_DATE', right_on='dt_iso')
    merged_df = merged_df.drop(
        columns=['dt_iso', 'feels_like', 'clouds_all', 'weather_main_encoded']
    )
    merged_df["USAGE_DATE"] = pd.to_datetime(merged_df["USAGE_DATE"])
    return merged_df


def call_the_weather_forecast():
    forecast = WeatherForecast()
    forecast_data = forecast.get_forecast()

    # Data augmentation
    forecast_data["day"] = forecast_data["dt_iso"].dt.day
    forecast_data["month"] = forecast_data["dt_iso"].dt.month
    forecast_data["day_of_week"] = forecast_data["dt_iso"].dt.dayofweek

    # Only keep noon forecasts, etc.
    forecast_data = forecast_data[forecast_data['dt_iso'].dt.hour == 12].copy()
    forecast_data['dt_iso'] = forecast_data['dt_iso'].dt.date

    # Map weather descriptions to numeric values
    weather_mapping = {
        'sky is clear': 0, 'few clouds': 1, 'scattered clouds': 2,
        'broken clouds': 3, 'overcast clouds': 4, 'light rain': 5,
        'moderate rain': 6, 'heavy intensity rain': 7,
        'light snow': 8, 'snow': 9
    }
    forecast_data['weather_description_encoded'] = forecast_data['weather_description'].map(weather_mapping)

    # Drop columns you don't need
    forecast_data = forecast_data.drop(
        columns=['humidity', 'feels_like', 'weather_main', 'weather_icon',
                 'clouds_all', 'weather_description']
    )

    # Scale numerical features
    scaler = MinMaxScaler()
    num_cols = ['temp', 'pressure', 'wind_speed']
    forecast_data[num_cols] = scaler.fit_transform(forecast_data[num_cols])

    forecast_data.rename(columns={'dt_iso': 'ds'}, inplace=True)

    # Prophet expects 'y' column for the target
    forecast_data['y'] = np.nan  # future attendance is unknown
    
    return forecast_data



# ---------------------------------------------------------------------------
# Main functions
# ---------------------------------------------------------------------------

def train_attendance_model(data, pre_covid=False):
    """
    Trains a Prophet model on historical attendance data, optionally
    excluding post-2022-01-01 data (pre_covid=True).

    Returns:
        model (Prophet): Trained Prophet model.
        df_train (pd.DataFrame): The training dataframe (Prophet-format: ds, y, and regressors).
    """

    # 1. Merge historical attendance with historical weather data
    df = data.attendance
    df_weather = data.weather
    merged_df = merge_for_attendance_forecasting(df, df_weather)

    # 2. Optionally filter out data after 2022-01-01
    if pre_covid:
        merged_df = merged_df[merged_df["USAGE_DATE"] < "2022-01-01"]

    # 3. Shift historical data so that its last date matches 'today' (or 'yesterday' if before noon)
    max_date = merged_df["USAGE_DATE"].max()
    now = datetime.now()
    target_date = (
        datetime.today().date()
        if now.hour >= 12
        else (datetime.today() - timedelta(days=1)).date()
    )
    days_to_shift = (pd.Timestamp(target_date) - max_date).days
    merged_df["USAGE_DATE"] = merged_df["USAGE_DATE"] + pd.Timedelta(days=days_to_shift)

    # Convert to date (rather than full datetime)
    merged_df['USAGE_DATE'] = merged_df['USAGE_DATE'].dt.date

    # 4. Rename columns for Prophet
    merged_df.rename(columns={'USAGE_DATE': 'ds', 'attendance': 'y'}, inplace=True)
    merged_df['ds'] = pd.to_datetime(merged_df['ds'])

    # 5. Sort by date
    merged_df.sort_values('ds', inplace=True)

    # 6. Separate rows with known attendance (train set)
    df_train = merged_df[~merged_df['y'].isna()].copy()

    # 7. Initialize and fit Prophet
    m = Prophet()
    # Add regressors
    m.add_regressor('temp')
    m.add_regressor('pressure')
    m.add_regressor('wind_speed')
    m.add_regressor('weather_description_encoded')
    m.add_regressor('day')
    m.add_regressor('month')
    m.add_regressor('day_of_week')

    m.fit(df_train)

    return m, df_train


def predict_attendance(model, days_to_predict=5):
    """
    Uses the trained Prophet model to forecast attendance for the specified
    number of days into the future, relying on actual weather forecasts.

    Args:
        model (Prophet): A fitted Prophet model.
        df_train (pd.DataFrame): The historical data used for training (in Prophet format).
        days_to_predict (int): Number of future days to forecast (default=5).

    Returns:
        forecast_future (pd.DataFrame): DataFrame containing at least ['ds', 'yhat'] with forecasts.
    """

    # 1. Get real weather forecast data
    forecast_data = call_the_weather_forecast()

    # 2. Combine historical (train) rows with future forecast rows
    #    This ensures that we have the same columns and Prophet can handle them properly.
    df_new = forecast_data
    df_new['y'] = np.nan  # future attendance is unknown
    # 3. Make sure columns align with Prophet's expectations
    #    Note: df_train was already renamed for Prophet, so let's rename forecast_data columns if needed.
    #    Since we already did rename in call_the_weather_forecast(), 
    #    we just ensure the final set of columns is consistent.
    df_new.rename(columns={'USAGE_DATE': 'ds'}, inplace=True)
    df_new['ds'] = pd.to_datetime(df_new['ds'])

    df_new.sort_values('ds', inplace=True)

    # 4. Future data = rows where 'y' is NaN
    df_future = df_new[df_new['y'].isna()].copy()

    # Optionally, you could limit df_future to only the next `days_to_predict` days:
    # df_future = df_future.iloc[:days_to_predict]

    # 5. Predict
    forecast_future = model.predict(df_future)

    # 6. Return only essential columns
    return forecast_future[['ds', 'yhat']]


## Usage example ##
data = DataLoader(load_all_files=True)
data.clean_data()
data.data_preprocessing()

# Train the model
model, df_train = train_attendance_model(data, pre_covid=False)

# Predict the next 5 days
forecast_result = predict_attendance(model, days_to_predict=5)
print(forecast_result)