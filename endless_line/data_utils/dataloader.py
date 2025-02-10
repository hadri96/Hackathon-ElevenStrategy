import os
from pathlib import Path
import git
import pandas as pd
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
		`load_all_files()` -> `None`: Load all the files in the data directory.
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
			return pd.read_csv(os.path.join(self.data_dir_path, file))
		elif file.endswith(".xlsx"):
			return pd.read_excel(os.path.join(self.data_dir_path, file))

	def clean_data(self):
		"""
  		Clean the data.
		"""
		self.clean_waiting_times()
		self.clean_weather()
		self.clean_parade_night_show()
		self.clean_entity_schedule()
		self.clean_link_attraction_park()
		self.clean_attendance()
		pass

	def clean_waiting_times(self):
		"""
		Clean the waiting times data.
		"""
		pass

	def clean_weather(self):
		self.weather['dt_iso'] = pd.to_datetime(self.weather['dt_iso'], format='%Y-%m-%d %H:%M:%S %z UTC', errors='coerce')
		self.weather['dt_iso'] = self.weather['dt_iso'].dt.tz_convert(None)
		columns_to_drop = ['weather_icon','grnd_level','sea_level','visibility']
		self.weather = self.weather.drop(columns=columns_to_drop)
		self.weather = self.weather[(self.weather['dt_iso'].dt.year.isin([2018, 2019])) | (self.weather['dt_iso'].dt.year >= 2022)]
		pass

	def clean_parade_night_show(self):
		"""
		Clean the parade and night show data.
		"""
		self.parade_night_show = self.parade_night_show[(self.parade_night_show['WORK_DATE'] < '2020-01-01') | (self.parade_night_show['WORK_DATE'] >= '2022-01-01')]
		pass

	def clean_entity_schedule(self):
		"""
		Clean the entity schedule data.
		"""
		attractions = self.link_attraction_park['ATTRACTION'].tolist()
		self.entity_schedule = self.entity_schedule[self.entity_schedule['ENTITY_DESCRIPTION_SHORT'].isin(attractions + ['PortAventura World'])]
		pass

	def clean_link_attraction_park(self):
		"""
		Clean the attraction-park mapping data.
		"""
		self.link_attraction_park = self.link_attraction_park[self.link_attraction_park['PARK'] == 'PortAventura World']
		pass

	def clean_attendance(self):
		"""
		Clean the attendance data.
		"""
		self.attendance = self.attendance[(self.attendance['USAGE_DATE'] < '2020-01-01') | (self.attendance['USAGE_DATE'] >= '2022-01-01')]
		self.attendance = self.attendance[self.attendance['FACILITY_NAME'] == 'PortAventura World']
		pass

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
		"""
		Preprocess the data.
		"""
		pass