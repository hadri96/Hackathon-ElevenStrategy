import os
from pathlib import Path
import git
import pandas as pd
import datetime
from sklearn.preprocessing import MinMaxScaler, LabelEncoder


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
	def __init__(self, data_dir_path: str = "data", load_all_files: bool = False):
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
		if load_all_files:
			self._load_all_files()
		

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
		files = os.listdir(self.data_dir_path)
		if file not in files:
			raise ValueError(f"File {file} not found in {self.data_dir_path}")
		if file.endswith(".csv"):
			if file == "link_attraction_park.csv":
				return pd.read_csv(os.path.join(self.data_dir_path, file), sep=";")
			return pd.read_csv(os.path.join(self.data_dir_path, file))
		elif file.endswith(".xlsx"):
			return pd.read_excel(os.path.join(self.data_dir_path, file))

	def clean_data(self):
		"""
  		Clean the data.
		"""
		self.clean_link_attraction_park() # pushed it to front. Given how we remove tivoli gardens data, it's better to put that here
		self.clean_waiting_times()
		self.clean_weather()
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

	def clean_parade_night_show(self):
		"""
		Clean the parade and night show data.
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
		# Careful: depending on how we join this with other table, it might mean that the parade is 30min or 45min long !!!!!
		parade_night_show_15 = parade_night_show_.copy()
		parade_night_show_30 = parade_night_show_.copy()
		time_change_15 = datetime.timedelta(minutes=15)
		time_change_30 = datetime.timedelta(minutes=30)
		parade_night_show_15['show_or_parade'] = parade_night_show_15['show_or_parade'].apply(lambda t: (datetime.datetime.combine(datetime.date.today(),t) + time_change_15).time())
		parade_night_show_30['show_or_parade'] = parade_night_show_30['show_or_parade'].apply(lambda t: (datetime.datetime.combine(datetime.date.today(),t) + time_change_30).time())
		
		# concat all the granular df into one
		parade_night_show_granular = pd.concat([parade_night_show_, parade_night_show_15, parade_night_show_30])

		# to merge this with time schedules, we need full datetimes (date + hour)
		parade_night_show_granular_ = parade_night_show_granular.copy()
		parade_night_show_granular_['show_or_parade'] = parade_night_show_granular_.apply(lambda row: pd.to_datetime(f"{row['WORK_DATE'].date()} {row['show_or_parade']}"), axis=1).astype('datetime64[s]')

		parade_night_show_granular_['WORK_DATE'] = parade_night_show_granular_['WORK_DATE'].astype('datetime64[s]')

		self.parade_night_show = parade_night_show_granular_.copy()

	def clean_entity_schedule(self):
		"""
		Clean the entity schedule data.
		"""
		attractions = self.link_attraction_park['ATTRACTION'].tolist()
		self.entity_schedule = self.entity_schedule[self.entity_schedule['ENTITY_DESCRIPTION_SHORT'].isin(attractions + ['PortAventura World'])]
		
		# modify date types
		self.entity_schedule["DEB_TIME"] = self.entity_schedule["DEB_TIME"].astype("datetime64[s]")
		self.entity_schedule["FIN_TIME"] = self.entity_schedule["FIN_TIME"].astype("datetime64[s]")
		self.entity_schedule["UPDATE_TIME"] = self.entity_schedule["UPDATE_TIME"].astype("datetime64[s]")
		self.entity_schedule["WORK_DATE"] = self.entity_schedule["WORK_DATE"].astype("datetime64[s]")


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
		pass

	def preprocess_waiting_times(self):
		"""
		Preprocess the data.
		"""
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

		# Normalize numerical columns
		scaler = MinMaxScaler()
		num_cols = ['temp', 'feels_like', 'pressure', 'wind_speed', 'clouds_all']
		self.weather[num_cols] = scaler.fit_transform(self.weather[num_cols])

		self.weather.loc[self.weather['dt_iso'].dt.year.isin([2018, 2019]), 'dt_iso'] += pd.DateOffset(years=2)

		self.weather['hour'] = self.weather['dt_iso'].dt.hour
		self.weather['day'] = self.weather['dt_iso'].dt.day
		self.weather['month'] = self.weather['dt_iso'].dt.month
		self.weather['day_of_week'] = self.weather['dt_iso'].dt.dayofweek



	def preprocess_parade_night_show(self):
		"""
		Preprocess the data.
		"""
		pass

	def preprocess_entity_schedule(self):
		"""
		Preprocess the data.
		"""
		pass

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
	

	def data_preprocessing_attendance_pred(self):
		"""
		Preprocess the data for the attedance prediction model.
		"""
		self.data_preprocessing()
		self.weather.drop(columns=['hour'], inplace=True)
		self.weather = self.weather[self.weather['dt_iso'].dt.hour == 12].copy()
		self.weather['dt_iso'] = self.weather['dt_iso'].dt.date
		pass