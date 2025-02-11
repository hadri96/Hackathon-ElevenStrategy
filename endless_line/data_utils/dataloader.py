import os
from pathlib import Path
import git
import pandas as pd
import datetime
from sklearn.preprocessing import MinMaxScaler


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
		self.clean_parade_night_show_attendance()
		self.clean_parade_night_show()
		self.clean_entity_schedule()
		self.clean_attendance()

	def clean_waiting_times(self):
		"""
		Clean the waiting times data.
		"""
		pass

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
		time_change_15 = datetime.timedelta(minutes=15)
		time_change_30 = datetime.timedelta(minutes=30)
		parade_night_show_15['show_or_parade'] = parade_night_show_15['show_or_parade'].apply(lambda t: (datetime.datetime.combine(datetime.date.today(),t) + time_change_15).time())
		parade_night_show_30['show_or_parade'] = parade_night_show_30['show_or_parade'].apply(lambda t: (datetime.datetime.combine(datetime.date.today(),t) + time_change_30).time())
		
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
		self.entity_schedule = self.entity_schedule[self.entity_schedule['ENTITY_DESCRIPTION_SHORT'].isin(attractions + ['PortAventura World'])]

		self.entity_schedule = self.entity_schedule[(self.entity_schedule['WORK_DATE'] < '2020-01-01') | (self.entity_schedule['WORK_DATE'] >= '2022-01-01')]
		
		# modify date types
		self.entity_schedule["DEB_TIME"] = self.entity_schedule["DEB_TIME"].astype("datetime64[s]")
		self.entity_schedule["FIN_TIME"] = self.entity_schedule["FIN_TIME"].astype("datetime64[s]")
		self.entity_schedule["UPDATE_TIME"] = self.entity_schedule["UPDATE_TIME"].astype("datetime64[s]")
		self.entity_schedule["WORK_DATE"] = self.entity_schedule["WORK_DATE"].astype("datetime64[s]")

		# entity_schedule (to clean waiting time)
		self.entity_schedule['IS_OPEN'] = self.entity_schedule['REF_CLOSING_DESCRIPTION'].isnull().astype(int)
		self.entity_schedule = self.entity_schedule[['WORK_DATE', 'ENTITY_DESCRIPTION_SHORT', 'IS_OPEN']]

		# entity_schedule
		self.entity_schedule_pivot = pd.pivot_table(self.entity_schedule, values='IS_OPEN', index=['WORK_DATE'], columns=['ENTITY_DESCRIPTION_SHORT'])
		self.entity_schedule_pivot = self.entity_schedule_pivot.reset_index()
		self.entity_schedule_pivot = self.entity_schedule_pivot.drop(columns='Vertical Drop')
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
		pass

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
		#Standardadising the attendance data beteen 0 to 1 using MinMaxScaler
		scaler = MinMaxScaler()
		self.attendance['attendance_normalized'] = scaler.fit_transform(self.attendance[['attendance']])
		#changing the date of the data to falsify 2021 and 2020 data to accomodate the model
		# Add 2 years to rows with year 2018 and 2019
		self.attendance.loc[self.attendance['USAGE_DATE'].dt.year.isin([2018, 2019]), 'USAGE_DATE'] += pd.DateOffset(years=2)

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
		return dt.replace(hour=rounded_minutes // 60, minute=rounded_minutes % 60)  # Convert back to time
	
