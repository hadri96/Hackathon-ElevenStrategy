import pandas as pd
import numpy as np
from endless_line.data_utils.dataloader import DataLoader
from endless_line.data_utils.weather_forecast import WeatherForecast
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from prophet import Prophet



data = DataLoader(load_all_files=True)
data.clean_data()
data.data_preprocessing_attendance_pred()

df = data.attendance
df_weather = data.weather

df_weather['dt_iso'] = pd.to_datetime(df_weather['dt_iso'])

# Merge the dataframes
merged_df = pd.merge(df, df_weather, left_on='USAGE_DATE', right_on='dt_iso')
merged_df = merged_df.drop(columns=['dt_iso', 'feels_like', 'clouds_all', 'weather_main_encoded'])
merged_df["USAGE_DATE"] = pd.to_datetime(merged_df["USAGE_DATE"])

# We now move the dataset to simulate the fact that it comes to 2025
# Get the maximum date in the dataset
max_date = merged_df["USAGE_DATE"].max()

# Determine target date (today if after noon, yesterday if before noon)
now = datetime.now()
target_date = datetime.today().date() if now.hour >= 12 else (datetime.today() - timedelta(days=1)).date()

# Compute the shift needed
days_to_shift = (pd.Timestamp(target_date) - max_date).days

# Apply the shift
merged_df["USAGE_DATE"] = merged_df["USAGE_DATE"] + pd.Timedelta(days=days_to_shift)

merged_df['USAGE_DATE'] = merged_df['USAGE_DATE'].dt.date


# We now need to get the weather data from the forecast, and preprocess it in a similar way
# Create an instance of the WeatherForecast class
forecast = WeatherForecast()
forecast_data = forecast.get_forecast()

# Data augmentation
forecast_data["day"] = forecast_data["dt_iso"].dt.day
forecast_data["month"] = forecast_data["dt_iso"].dt.month
forecast_data["day_of_week"] = forecast_data["dt_iso"].dt.dayofweek

# Data preprocessing
forecast_data = forecast_data[forecast_data['dt_iso'].dt.hour == 12].copy()
forecast_data['dt_iso'] = forecast_data['dt_iso'].dt.date
weather_mapping = {
			'sky is clear': 0,
			'few clouds': 1,
			'scattered clouds': 2,
			'broken clouds': 3,
			'overcast clouds': 4,
			'light rain': 5,
			'moderate rain': 6,
			'heavy intensity rain': 7,
			'light snow': 8,
			'snow': 9
		}
forecast_data['weather_description_encoded'] = forecast_data['weather_description'].map(weather_mapping)
forecast_data = forecast_data.drop(columns=['humidity', 'feels_like', 'weather_main', 'weather_icon', 'clouds_all', 'weather_description'])

scaler = MinMaxScaler()
num_cols = ['temp', 'pressure', 'wind_speed']
forecast_data[num_cols] = scaler.fit_transform(forecast_data[num_cols])

# We now merge the historical data with the forecast data
forecast_data.rename(columns={'dt_iso': 'USAGE_DATE'}, inplace=True)

# Add a column attendance with null values to forecast_data
forecast_data['attendance'] = np.nan

# Concatenate merged_df with forecast_data
combined_df = pd.concat([merged_df, forecast_data], ignore_index=True)


# We now implement the Prophet model
df_new = combined_df.copy()

# Rename columns if needed for Prophet
df_new.rename(columns={'USAGE_DATE': 'ds', 'attendance': 'y'}, inplace=True)

# Ensure ds is datetime and sorted by ds
df_new['ds'] = pd.to_datetime(df_new['ds'])
df_new.sort_values('ds', inplace=True)

# Separate the rows we can use to train (non-NaN in 'y')
df_train = df_new[~df_new['y'].isna()].copy()

# Separate the rows we want to predict (NaN in 'y') -- last 5 days
df_future = df_new[df_new['y'].isna()].copy()

m = Prophet()

# Add extra regressors just like before
m.add_regressor('temp')
m.add_regressor('pressure')
m.add_regressor('wind_speed')
m.add_regressor('weather_description_encoded')
m.add_regressor('day')
m.add_regressor('month')
m.add_regressor('day_of_week')

# Fit on df_train only (the rows where attendance is known)
m.fit(df_train)

forecast_future = m.predict(df_future)

# forecast_future will include columns like 'yhat', 'yhat_lower', 'yhat_upper', etc.
print(forecast_future[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])