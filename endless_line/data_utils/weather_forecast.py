from dotenv import load_dotenv
import os
import requests
import pandas as pd
from endless_line.data_utils.dataloader import DataLoader

class WeatherForecast:
	def __init__(self):
		"""
		Initialize the WeatherForecast class.
		"""
		data = DataLoader()
		if load_dotenv(os.path.join(data.root_dir, '.secret')):
			self.weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
		else:
			raise ValueError(".secret file not found, please create .secret file in the root directory with your API keys")

	def get_forecast(self, lat: float=48.873492, lon: float=2.295104):
		url = 'https://api.openweathermap.org/data/2.5/forecast?'
		params = {
					'lat': lat,
					'lon': lon,
					'units': 'metric',
					'appid': self.weather_api_key
		}
		forecast = requests.get(url, params=params).json()
		return self.clean_forecast(forecast)

	def clean_forecast(self, forecast):
		"""
		Clean the forecast data.
		"""
		# Clean forecast data
		for stamp in forecast['list']:
			for info in stamp['main']:
				if info in ['sea_level', 'grnd_level', 'temp_min', 'temp_max', 'temp_kf']:
					continue
				stamp[info] = stamp['main'][info]
			# Matching weather description
			match_description = {
				'clear sky': 'sky is clear',
				'few clouds: 11-25%': 'few clouds',
				'scattered clouds: 25-50%': 'scattered clouds',
				'broken clouds: 51-84%': 'broken clouds',
				'overcast clouds: 85-100%': 'overcast clouds',
			}
			for info in stamp['weather'][0]:
				if info in ['id']:
					continue
				elif info == 'description':
					stamp[f'weather_{info}'] = match_description.get(stamp['weather'][0]['description'], stamp['weather'][0]['description'])
				else:
					stamp[f'weather_{info}'] = stamp['weather'][0][info]
			# Add clouds and wind speed
			stamp['clouds_all'] = stamp['clouds']['all']
			stamp['wind_speed'] = stamp['wind']['speed']
			# Remove useless keys
			keys_to_remove = {'sys', 'rain', 'weather', 'clouds', 'main', 'wind', 'pop', 'dt', 'visibility'}
			for key in keys_to_remove:
				stamp.pop(key, None)

		forecast_df = pd.DataFrame(forecast['list'])
		forecast_df['dt_txt'] = pd.to_datetime(forecast_df['dt_txt'], format='%Y-%m-%d %H:%M:%S')
		forecast_df.rename(columns={'dt_txt': 'dt_iso'}, inplace=True)
		# Resample and interpolate 3-hourly data to hourly data with forward fill
		forecast_df = forecast_df.set_index('dt_iso').resample('h').interpolate(method='ffill', limit_direction='forward')
		forecast_df.reset_index(inplace=True)
		## TO DO CHECK OPENING TIMES OF PARK AND REMOVE DATA OUTSIDE OF OPENING TIMES
		return forecast_df
