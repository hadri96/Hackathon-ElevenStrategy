import os
from pathlib import Path
import git
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import boto3
from botocore.config import Config
from dotenv import load_dotenv
import os
from io import StringIO
import numpy as np

class DataLoader:
	"""A class to handle loading data files from a specified directory.

	This class provides functionality to load data files from a specified directory,
	automatically resolving paths relative to the git repository root. It supports
	loading CSV and Excel files.

	Attributes
	----------
		`root_dir` (`str`): The absolute path to the git repository root.
		`data_dir_path` (`str`): The full path to the data directory.
		`attendance` (`pd.DataFrame`): Attendance data if `load_all_files=True`.
		`entity_schedule` (`pd.DataFrame`): Entity schedule data if `load_all_files=True`.
		`link_attraction_park` (`pd.DataFrame`): Attraction-park mapping if `load_all_files=True`.
		`weather` (`pd.DataFrame`): Weather data if `load_all_files=True`.
		`waiting_times` (`pd.DataFrame`): Waiting times data if `load_all_files=True`.
		`parade_night_show` (`pd.DataFrame`): Parade/show data if `load_all_files=True`.

	Methods
	-------
		`load_file(file: str)` -> `pd.DataFrame`: Load a single file from the data directory.
		`load_all_files()` -> `None`: Load all the files in the data directory.¨
		`clean_data()` -> `None`: Clean the data.
	"""
	def __init__(self, data_dir_path: str = "data", load_all_files: bool = False, clean_data: bool = False, db: bool = False):
		"""Initializes the DataLoader.

	Args:
		data_dir_path (str): The path to the data directory.
		load_all_files (bool, optional): Whether to load all files in the data directory.
			If True, the following class attributes will be populated with data:
			\n\t - `attendance`: Attendance data.
			\n\t - `entity_schedule`: Entity schedule data.
			\n\t - `link_attraction_park`: Attraction-park mapping.
			\n\t - `weather`: Weather data.
			\n\t - `waiting_times`: Waiting times data.
			\n\t - `parade_night_show`: Parade and night show data.
			Defaults to False.
	"""
		self.root_dir = self._find_git_root()
		self.data_dir_path = os.path.join(self.root_dir, data_dir_path)
		if load_all_files and not db:
			self._load_all_files()
		if clean_data:
			self.clean_data()
		self.db = db


	def _find_git_root(self) -> str:
		"""Find the root directory of the git repository.

		Returns
		-------
			`str`: Absolute path to the git root directory

		Raises
		-------
			`git.exc.InvalidGitRepositoryError`: If not in a git repository
		"""
		try:
			git_repo = git.Repo(Path.cwd(), search_parent_directories=True)
			return git_repo.git.rev_parse("--show-toplevel")
		except git.exc.InvalidGitRepositoryError:
			raise git.exc.InvalidGitRepositoryError(
				"Not a git repository. Please run from within the project repository."
			)

	def _load_all_files(self) -> pd.DataFrame:
		"""
		Load all the files in the data directory.
		"""
		self.attendance = pd.read_csv(os.path.join(self.data_dir_path, "attendance.csv"))
		self.entity_schedule = pd.read_csv(os.path.join(self.data_dir_path, "entity_schedule.csv"))
		self.link_attraction_park = pd.read_csv(os.path.join(self.data_dir_path, "link_attraction_park.csv"), sep=";")
		self.weather = pd.read_csv(os.path.join(self.data_dir_path, "weather_data.csv"))
		self.waiting_times = pd.read_csv(os.path.join(self.data_dir_path, "waiting_times.csv"))
		self.parade_night_show = pd.read_excel(os.path.join(self.data_dir_path, "parade_night_show.xlsx"), index_col=0)

	def load_file(self, file: str) -> pd.DataFrame:
		"""Load the data from the data directory.

		Args
		-------
			`file` (`str`): The name of the file to load.

		Returns
		-------
			`pd.DataFrame`: The loaded data

		Raises
		-------
			`ValueError`: If the file is not found in the data directory
		"""
		if self.db:
			return self.load_file_db(file)
		files = os.listdir(self.data_dir_path)
		if file not in files:
			raise ValueError(f"File {file} not found in {self.data_dir_path}")
		if file.endswith(".csv"):
			if file == "link_attraction_park.csv":
				return pd.read_csv(os.path.join(self.data_dir_path, file), sep=";")
			return pd.read_csv(os.path.join(self.data_dir_path, file))
		elif file.endswith(".xlsx"):
			return pd.read_excel(os.path.join(self.data_dir_path, file))

	def load_file_db(self, file: str) -> pd.DataFrame:
		load_dotenv(os.path.join(self.root_dir, '.secret'))
		if not file.endswith(".csv"):
			raise ValueError(f"File {file} is not a data file")

		key_id = os.getenv('B2keyID')
		db_name = os.getenv('B2DBNAME')
		key_name = os.getenv('B2keyNAME')
		key_app_key = os.getenv('B2keyAPPKEY')
		endpoint = os.getenv('B2endpoint')
		if not key_id or not db_name or not key_name or not key_app_key or not endpoint:
			raise ValueError("Environment variables not set")
		config = Config(signature_version='s3v4')
		s3 = boto3.resource(service_name='s3',
						  config=config,
						  endpoint_url=endpoint,
						  aws_access_key_id=key_id,
						  aws_secret_access_key=key_app_key)
		bucket = s3.Bucket(db_name)
		if file not in [obj.key for obj in bucket.objects.all()]:
			raise ValueError(f"File {file} not found in {db_name}")
		obj = s3.Object(db_name, file)
		csv_data = obj.get()['Body'].read().decode('utf-8')
		if file == "link_attraction_park.csv":
			return pd.read_csv(StringIO(csv_data), sep=";")
		elif file == "parade_night_show.xlsx":
			return pd.read_excel(os.path.join(self.data_dir_path, "parade_night_show.xlsx"), index_col=0)
		else:
			return pd.read_csv(StringIO(csv_data))


	def clean_data(self):
		"""
		Clean the data.
		"""
		self.clean_link_attraction_park() # pushed it to front. Given how we remove tivoli gardens data, it's better to put that here
		self.clean_waiting_times()
		self.clean_weather()
		self.clean_parade_night_show_attendance()
		self.clean_parade_night_show()
		self.clean_entity_schedule()
		self.clean_attendance()

	def clean_waiting_times(self):
		"""
		Filters a pandas DataFrame 'waiting_times' to exclude rows where 'WORK_DATE'
		falls between '01/01/2020' and '31/12/2021' (inclusive).

		Args:
			df: pandas DataFrame with a 'WORK_DATE' column.

		Returns:
			pandas DataFrame: A new DataFrame with rows filtered based on 'WORK_DATE'.
							Returns None if 'WORK_DATE' column is not found.
		"""
		df = self.waiting_times

		for col in df.columns:
			if pd.api.types.is_numeric_dtype(df[col]): # Check if the column is numeric
				negative_mask = df[col] < 0
				df.loc[negative_mask, col] = 0

		if 'WORK_DATE' not in df.columns:
			print("Error: 'WORK_DATE' column not found in the DataFrame.")
			return None
		
		# Convert DEB_TIME and FIN_TIME to datetime
		df["DEB_TIME"] = df["DEB_TIME"].astype("datetime64[s]")
		df["FIN_TIME"] = df["FIN_TIME"].astype("datetime64[s]")

		# Convert 'WORK_DATE' to datetime objects.
		# Assuming 'WORK_DATE' is in DD/MM/YYYY format. Adjust format if necessary.
		try:
			df['WORK_DATE'] = pd.to_datetime(df['WORK_DATE'], format='%Y-%m-%d', errors='coerce')
		except ValueError:
			print("Error: Could not convert 'WORK_DATE' to datetime. Please check the date format in your 'WORK_DATE' column.")
			return None

		if df['WORK_DATE'].isnull().any():
			print("Warning: Some 'WORK_DATE' values could not be converted to datetime and will be treated as NaT. Please check date formats.")


		# Define the start and end dates for exclusion
		start_date = pd.to_datetime('01/01/2020', format='%d/%m/%Y')
		end_date = pd.to_datetime('31/12/2021', format='%d/%m/%Y')

		# Filter the DataFrame to exclude rows within the specified date range
		filtered_df = df[~((df['WORK_DATE'] >= start_date) & (df['WORK_DATE'] <= end_date))]

		if 'GUEST_CARRIED' not in df.columns:
			print("Error: 'GUEST_CARRIED' column not found in the DataFrame.")

		# Calculate mean and standard deviation
		mean_guest_carried = filtered_df['GUEST_CARRIED'].mean()
		std_guest_carried = filtered_df['GUEST_CARRIED'].std()

		# Define outlier boundaries (3 standard deviations from the mean)
		upper_bound = mean_guest_carried + 5 * std_guest_carried

		# Identify outliers
		outlier_mask = (filtered_df['GUEST_CARRIED'] > upper_bound)

		# Replace outliers with the mean
		filtered_df.loc[outlier_mask, 'GUEST_CARRIED'] = mean_guest_carried

		# filter attractions to only keep port aventura world
		attractions = self.link_attraction_park['ATTRACTION'].tolist()
		attractions.remove('Vertical Drop')
		filtered_df = filtered_df[filtered_df['ENTITY_DESCRIPTION_SHORT'].isin(attractions + ['PortAventura World'])]

		self.waiting_times = filtered_df

	def clean_weather(self):
		self.weather['dt_iso'] = pd.to_datetime(
			self.weather['dt_iso'], format='%Y-%m-%d %H:%M:%S %z UTC', errors='coerce'
		)
		self.weather['dt_iso'] = self.weather['dt_iso'].dt.tz_localize(None)

		columns_to_drop = [
			'dew_point', 'temp_min', 'temp_max', 'humidity', 'weather_icon', 'rain_1h',
			'rain_3h', 'grnd_level', 'sea_level', 'visibility', 'dt', 'timezone',
			'city_name', 'lat', 'lon', 'snow_1h', 'snow_3h', 'wind_deg', 'wind_gust', 'weather_id'
		]

		self.weather = self.weather.drop(columns=columns_to_drop, errors='ignore')
		self.weather = self.weather[
			(self.weather['dt_iso'].dt.year.isin([2018, 2019])) | (self.weather['dt_iso'].dt.year >= 2022)
		]

	def clean_parade_night_show_attendance(self):
		"""
		Clean the parade and night show data for attendance prediction.
		"""
		self.parade_night_show_attendance = self.parade_night_show[(self.parade_night_show['WORK_DATE'] < '2020-01-01') | (self.parade_night_show['WORK_DATE'] >= '2022-01-01')]
		self.parade_night_show_attendance["Num_parade"] = 3 - self.parade_night_show_attendance[["NIGHT_SHOW",	"PARADE_1",	"PARADE_2"]].isna().sum(axis=1)
		self.parade_night_show_attendance = self.parade_night_show_attendance[["WORK_DATE", "Num_parade"]]
		

	def clean_parade_night_show(self):
		"""
		Clean the parade and night show data for waiting time prediction.
		"""
		self.parade_night_show = self.parade_night_show[(self.parade_night_show['WORK_DATE'] < '2020-01-01') | (self.parade_night_show['WORK_DATE'] >= '2022-01-01')]

		# create 3 separate df for each parade type, in order to concat everything
		parade_night_show_night_show = self.parade_night_show[["WORK_DATE", "NIGHT_SHOW"]].rename(columns={"NIGHT_SHOW": 'show_or_parade'})
		parade_night_show_parade_1 = self.parade_night_show[["WORK_DATE", "PARADE_1"]].rename(columns={"PARADE_1": 'show_or_parade'})
		parade_night_show_parade_2 = self.parade_night_show[["WORK_DATE", "PARADE_2"]].rename(columns={"PARADE_2": 'show_or_parade'})

		parade_night_show_ = pd.concat([parade_night_show_night_show, parade_night_show_parade_1, parade_night_show_parade_2])

		# drop all rows of non-existing parades and shows (nan values)
		parade_night_show_ = parade_night_show_.dropna(subset=['show_or_parade'])

		# create 15min granularity (to join with other tables) on separate dataframes
		# Careful: here the behaviour with round and non-round times is not the same
		parade_night_show_15 = parade_night_show_.copy()
		parade_night_show_30 = parade_night_show_.copy()
		# intermediary step: a parade is 30min, so depending on whether the minute of start is round or not, we need to create a 30min or a 45min time span 
		round_times = [00, 15, 30, 45]
		parade_night_show_30 = parade_night_show_30[parade_night_show_30['show_or_parade'].apply(lambda t: t.minute not in round_times)]
		# adding 15 and 30 min deltas
		time_change_15 = timedelta(minutes=15)
		time_change_30 = timedelta(minutes=30)

		parade_night_show_15['show_or_parade'] = parade_night_show_15['show_or_parade'].apply(
			lambda t: (datetime.combine(datetime.today(), t) + time_change_15).time()
		)

		parade_night_show_30['show_or_parade'] = parade_night_show_30['show_or_parade'].apply(
			lambda t: (datetime.combine(datetime.today(), t) + time_change_30).time()
		)

		# concat all the granular df into one
		parade_night_show_ = pd.concat([parade_night_show_, parade_night_show_15, parade_night_show_30])

		# to merge this with waiting times, we need full datetimes (date + hour)
		parade_night_show_['show_or_parade'] = parade_night_show_.apply(lambda row: pd.to_datetime(f"{row['WORK_DATE'].date()} {row['show_or_parade']}"), axis=1).astype('datetime64[s]')

		# round down the minutes (to match with DEB_TIME in waiting times table)
		parade_night_show_['show_or_parade'] = parade_night_show_['show_or_parade'].apply(lambda dt: self.round_to_quarter(dt, down=True))

		parade_night_show_['WORK_DATE'] = parade_night_show_['WORK_DATE'].astype('datetime64[s]')

		self.parade_night_show = parade_night_show_.copy()

	def clean_entity_schedule(self):
		"""
		Clean the entity schedule data.
		"""
		attractions = self.link_attraction_park['ATTRACTION'].tolist()
		attractions.remove('Vertical Drop')
		self.entity_schedule = self.entity_schedule[self.entity_schedule['ENTITY_DESCRIPTION_SHORT'].isin(attractions)] # + ['PortAventura World']

		self.entity_schedule = self.entity_schedule[(self.entity_schedule['WORK_DATE'] < '2020-01-01') | (self.entity_schedule['WORK_DATE'] >= '2022-01-01')]

		# modify date types
		self.entity_schedule["DEB_TIME"] = self.entity_schedule["DEB_TIME"].astype("datetime64[s]")
		self.entity_schedule["FIN_TIME"] = self.entity_schedule["FIN_TIME"].astype("datetime64[s]")
		self.entity_schedule["UPDATE_TIME"] = self.entity_schedule["UPDATE_TIME"].astype("datetime64[s]")
		self.entity_schedule["WORK_DATE"] = self.entity_schedule["WORK_DATE"].astype("datetime64[s]")

		# entity_schedule to clean waiting time
		self.entity_schedule['IS_OPEN'] = self.entity_schedule['REF_CLOSING_DESCRIPTION'].isnull().astype(int)
		self.entity_schedule = self.entity_schedule[['WORK_DATE', 'ENTITY_DESCRIPTION_SHORT', 'IS_OPEN']]

		# entity_schedule as pivot table
		self.entity_schedule_pivot = pd.pivot_table(self.entity_schedule, values='IS_OPEN', index=['WORK_DATE'], columns=['ENTITY_DESCRIPTION_SHORT'])
		self.entity_schedule_pivot.columns.name = None
		self.entity_schedule_pivot = self.entity_schedule_pivot.reset_index()
		
		# dealing with NaN values
		#self.entity_schedule_pivot = self.entity_schedule_pivot.drop(columns='Vertical Drop')
		self.entity_schedule_pivot = self.entity_schedule_pivot.bfill()



	def clean_link_attraction_park(self):
		"""
		Clean the attraction-park mapping data.
		"""
		self.link_attraction_park = self.link_attraction_park[self.link_attraction_park['PARK'] == 'PortAventura World']

	def clean_attendance(self):
		"""
		Clean the attendance data.
		"""
		self.attendance = self.attendance[(self.attendance['USAGE_DATE'] < '2020-01-01') | (self.attendance['USAGE_DATE'] >= '2022-01-01')]
		self.attendance = self.attendance[self.attendance['FACILITY_NAME'] == 'PortAventura World']
		self.attendance['USAGE_DATE'] = pd.to_datetime(self.attendance['USAGE_DATE'])

	def data_preprocessing(self):
		"""
		Preprocess the data.
		"""
		self.preprocess_weather()
		self.preprocess_attendance()
		self.preprocess_waiting_times()
		self.preprocess_entity_schedule()
		self.preprocess_link_attraction_park()
		self.preprocess_parade_night_show()
		self.preprocess_parade_night_show_attendance()

	def preprocess_waiting_times(self):
		"""
		Preprocess the data.
		"""
		self.waiting_times.loc[self.waiting_times['WORK_DATE'].dt.year.isin([2018, 2019]), 'WORK_DATE'] += pd.DateOffset(years=2)
		self.waiting_times.loc[self.waiting_times['DEB_TIME'].dt.year.isin([2018, 2019]), 'DEB_TIME'] += pd.DateOffset(years=2)
		self.waiting_times.loc[self.waiting_times['FIN_TIME'].dt.year.isin([2018, 2019]), 'FIN_TIME'] += pd.DateOffset(years=2)
		self.waiting_times = self.waiting_times.drop(columns=["CAPACITY"])
		attractions = self.link_attraction_park['ATTRACTION'].tolist()
		self.waiting_times = self.waiting_times[self.waiting_times['ENTITY_DESCRIPTION_SHORT'].isin(attractions + ['PortAventura World'])]
		#self.waiting_times = self.waiting_times[~((self.waiting_times['OPEN_TIME'].isnull()) & (self.waiting_times['WAIT_TIME_MAX'].isnull()))] # drop lines when closed
		pass

	def preprocess_weather(self):
		"""
		Preprocess the data.
		"""
		label_enc_main = LabelEncoder()
		label_enc_desc = LabelEncoder()

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

		self.weather['weather_description_encoded'] = self.weather['weather_description'].map(weather_mapping)
		self.weather['weather_main_encoded'] = label_enc_main.fit_transform(self.weather['weather_main'])

		# Drop original categorical columns
		self.weather.drop(columns=['weather_main', 'weather_description'], inplace=True)

		self.weather.loc[self.weather['dt_iso'].dt.year.isin([2018, 2019]), 'dt_iso'] += pd.DateOffset(years=2)

		self.weather['minute'] = self.weather['dt_iso'].dt.minute
		self.weather['hour'] = self.weather['dt_iso'].dt.hour
		self.weather['day'] = self.weather['dt_iso'].dt.day
		self.weather['month'] = self.weather['dt_iso'].dt.month
		self.weather['day_of_week'] = self.weather['dt_iso'].dt.dayofweek
		self.weather['is_weekend'] = self.weather['dt_iso'].dt.dayofweek.isin([5, 6]).astype(int)
		self.weather['is_peak_hour'] = self.weather['hour'].between(11, 18).astype(int)



	def preprocess_parade_night_show(self):
		"""
		Preprocess the data.
		"""
		self.parade_night_show = self.parade_night_show.drop(columns='WORK_DATE')
		self.parade_night_show.loc[self.parade_night_show['show_or_parade'].dt.year.isin([2018, 2019]), 'show_or_parade'] += pd.DateOffset(years=2)
		#self.parade_night_show.loc[self.parade_night_show['WORK_DATE'].dt.year.isin([2018, 2019]), 'WORK_DATE'] += pd.DateOffset(years=2)
		pass

	def preprocess_parade_night_show_attendance(self):
		"""
		Preprocess the data.
	
		"""
		self.parade_night_show_attendance.loc[self.parade_night_show_attendance['WORK_DATE'].dt.year.isin([2018, 2019]), 'WORK_DATE'] += pd.DateOffset(years=2)

	def preprocess_entity_schedule(self):
		"""
		Preprocess the data.

		"""
		# currently we have dropped those columns
		"""self.entity_schedule.loc[self.entity_schedule['DEB_TIME'].dt.year.isin([2018, 2019]), 'DEB_TIME'] += pd.DateOffset(years=2)
		self.entity_schedule.loc[self.entity_schedule['FIN_TIME'].dt.year.isin([2018, 2019]), 'FIN_TIME'] += pd.DateOffset(years=2)
		self.entity_schedule.loc[self.entity_schedule['UPDATE_TIME'].dt.year.isin([2018, 2019]), 'UPDATE_TIME'] += pd.DateOffset(years=2)"""
		self.entity_schedule.loc[self.entity_schedule['WORK_DATE'].dt.year.isin([2018, 2019]), 'WORK_DATE'] += pd.DateOffset(years=2)
		self.entity_schedule_pivot.loc[self.entity_schedule_pivot['WORK_DATE'].dt.year.isin([2018, 2019]), 'WORK_DATE'] += pd.DateOffset(years=2)
		self.entity_schedule_pivot = self.entity_schedule_pivot.set_index('WORK_DATE')

		# Define start and end dates
		start_date = np.datetime64('2022-01-01')
		end_date = np.datetime64('2022-03-31')

		# Generate an array of dates
		date_range = np.arange(start_date, end_date + np.timedelta64(1, 'D'), dtype='datetime64[D]')
		date_range_seconds = date_range.astype('datetime64[s]')

		# create empty entity_schedule_pivot with only the missing dates
		df_missing_schedule = pd.DataFrame({'WORK_DATE': date_range_seconds}).set_index('WORK_DATE')
		df_missing_schedule = df_missing_schedule.merge(self.entity_schedule_pivot, on='WORK_DATE', how='left').fillna(0)

		# retrieve only the useful rows from self.waiting_times
		waiting_times = self.waiting_times[(self.waiting_times['WORK_DATE'] >= '2022-01-01') & (self.waiting_times['WORK_DATE'] <= '2022-03-31')]
		waiting_times.shape

		# iterate on waiting times, and if an attraction was used at least once on that day, mark the attraction as open for that day
		for index, row in waiting_times.iterrows():
			if row['ENTITY_DESCRIPTION_SHORT'] in list(df_missing_schedule.columns):
				if row['OPEN_TIME'] != 0:
					df_missing_schedule.loc[row['WORK_DATE'], row['ENTITY_DESCRIPTION_SHORT']] = 1

		# concatenate it with existing entity_schedule_pivot
		self.entity_schedule_pivot = pd.concat([self.entity_schedule_pivot, df_missing_schedule]).sort_values('WORK_DATE')

		# melt the pivoted missing schedule to match entity_schedule table
		df_missing_schedule_ = df_missing_schedule.copy().reset_index()
		df_melt = pd.melt(df_missing_schedule_, id_vars='WORK_DATE', var_name='ENTITY_DESCRIPTION_SHORT', value_name='IS_OPEN')
		self.entity_schedule = pd.concat([self.entity_schedule, df_melt])

	def preprocess_link_attraction_park(self):
		"""
		Preprocess the data.
		"""
		pass

	def preprocess_attendance(self):
		self.attendance['USAGE_DATE'] = pd.to_datetime(self.attendance['USAGE_DATE'])
		self.attendance.drop_duplicates(inplace=True)
		self.attendance.drop(columns=['FACILITY_NAME'], inplace=True)
		#changing the date of the data to falsify 2021 and 2020 data to accomodate the model
		# Add 2 years to rows with year 2018 and 2019
		self.attendance.loc[self.attendance['USAGE_DATE'].dt.year.isin([2018, 2019]), 'USAGE_DATE'] += pd.DateOffset(years=2)

	def merge(self):
		"""
			Merge all tables for model.
		"""
		self.merge_parade_night_show()
		self.merge_parade_night_show_attendance()
		self.merge_entity_schedule_pivot()
		self.merge_entity_schedule()
		self.merge_weather()
		self.merge_attendance()
		self.scale_and_move_to_2025()
		
		
	def merge_parade_night_show(self):
		"""
			merge waiting_times with parade_night_show
		"""
		self.merged = self.waiting_times.merge(self.parade_night_show, left_on='DEB_TIME', right_on='show_or_parade', how='left')
		self.merged['show_or_parade'] = self.merged['show_or_parade'].notnull().astype(int)
		
	def merge_parade_night_show_attendance(self):
		"""
			merge waiting_times with parade_night_show_attendance
			it deals with post covid null values by saying there was no parade on first 3 months of 2022.
		"""
		self.merged = self.merged.merge(self.parade_night_show_attendance, left_on='WORK_DATE', right_on='WORK_DATE', how='left')
		self.merged['Num_parade'] = self.merged['Num_parade'].fillna(0)

	def merge_entity_schedule_pivot(self):
		"""
			merge waiting_times with entity_schedule_pivot
		"""
		self.merged = self.merged.merge(self.entity_schedule_pivot, left_on='WORK_DATE', right_on='WORK_DATE', how='left')
		self.merged = self.merged.sort_values('DEB_TIME').bfill()

	def merge_entity_schedule(self):
		"""
			merge waiting_times with entity_schedule
		"""
		self.merged = self.merged.merge(self.entity_schedule, left_on=['WORK_DATE', 'ENTITY_DESCRIPTION_SHORT'], right_on=['WORK_DATE', 'ENTITY_DESCRIPTION_SHORT'], how='left')
		self.merged = self.merged.sort_values('DEB_TIME').bfill()

	def merge_weather(self):
		"""
			merge waiting_times with weather
		"""
		self.merged["DEB_TIME_2"] = pd.to_datetime(self.merged["WORK_DATE"]) + pd.to_timedelta(self.merged["DEB_TIME_HOUR"], unit="h")
		self.weather["dt_iso"] = pd.to_datetime(self.weather["dt_iso"])

		# Merge on matching datetime values
		self.merged = self.merged.merge(self.weather, left_on="DEB_TIME_2", right_on="dt_iso", how="left")

		self.merged.drop(columns=["dt_iso", "DEB_TIME_2"], inplace=True)
		self.merged = self.merged.sort_values('DEB_TIME').bfill()

	def merge_attendance(self):
		"""
			merge waiting_times with attendance
		"""
		self.merged = self.merged.merge(self.attendance, left_on='WORK_DATE', right_on='USAGE_DATE', how='left').drop(columns='USAGE_DATE')


	def scale_and_move_to_2025(self):
		"""
		Scale the data (only for rows up to 2021-12-23) and then move it so that the last date aligns with 'today' (if after noon) or 'yesterday' (if before noon).
		"""

		# Filter data up to 2021-12-23
		self.merged = self.merged[self.merged["WORK_DATE"] <= pd.Timestamp(2021, 12, 12)].copy()

		# List of numerical columns that should be scaled
		numerical_columns = [
			'GUEST_CARRIED', 'ADJUST_CAPACITY', 'OPEN_TIME', 'UP_TIME', 
			'DOWNTIME', 'NB_MAX_UNIT', 'Num_parade', 'NB_UNITS', 
			'temp', 'feels_like', 'pressure', 'wind_speed', 'clouds_all', 
			'weather_description_encoded', 'weather_main_encoded', 
			'minute', 'hour', 'day', 'month', 'day_of_week', 'attendance'
		]

		# Scale numerical columns with MinMaxScaler
		scaler = MinMaxScaler()
		self.merged[numerical_columns] = scaler.fit_transform(self.merged[numerical_columns])

		# Get the maximum date in the filtered dataset
		max_date = self.merged["WORK_DATE"].max()

		# Determine target date (today if after noon, yesterday if before noon)
		now = datetime.now()
		target_date = datetime.today().date() if now.hour >= 12 else (datetime.today() - timedelta(days=1)).date()

		# Compute the shift needed
		days_to_shift = (pd.Timestamp(target_date) - max_date).days

		# Apply the shift to the relevant columns
		self.merged["WORK_DATE"] = self.merged["WORK_DATE"] + pd.Timedelta(days=days_to_shift)
		self.merged["WORK_DATE"] = self.merged["WORK_DATE"].dt.date

		self.merged["DEB_TIME"] = self.merged["DEB_TIME"] + pd.Timedelta(days=days_to_shift)
		self.merged["FIN_TIME"] = self.merged["FIN_TIME"] + pd.Timedelta(days=days_to_shift)

	def round_to_quarter(self, dt, down=True):
		"""
			Takes datetime64 as input (e.g. 9:10).
			Rounds in down to the lower round time (e.g. 9:00).
			Returns a datetime64
		"""
		minutes = dt.hour * 60 + dt.minute  # Convert time to total minutes
		minutes += 0 if down else 14  # rounding down => nothing to do / rounding up => add 14min
		rounded_minutes = (minutes // 15) * 15  # Round down to nearest quarter
		if down:
			rounded_minutes = max(rounded_minutes, 15) # avoid going below midnight
		else:
			rounded_minutes = min(rounded_minutes, 23 * 60 + 45)  # avoid going above midnight
		return dt.replace(hour=rounded_minutes // 60, minute=rounded_minutes % 60)  # Convert back to datetime


	def data_preprocessing_attendance_pred(self):
		"""
		Preprocess the data for the attedance prediction model.
		"""
		self.weather.drop(columns=['hour'], inplace=True)
		self.weather = self.weather[self.weather['dt_iso'].dt.hour == 12].copy()
		self.weather['dt_iso'] = self.weather['dt_iso'].dt.date
		pass
