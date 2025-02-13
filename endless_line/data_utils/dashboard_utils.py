from endless_line.data_utils.dataloader import DataLoader
from endless_line.models.attendance_model import predict_attendance
from datetime import datetime, timedelta
import pandas as pd

class DashboardUtils:
	"""
	DashboardUtils class provides utility functions to interact with the data loaded by DataLoader.
	Methods
	-------
	get_attractions() -> list:
		Returns a list of unique attractions
	get_attendance(df, date) -> int:
		Returns the attendance for a given date, as predicted by the forecasted df
	compute_kpi(df, attractions=None) -> str:
		Returns some KPIs based on business needs
		Available kpi numbers : 1, 2, 3
	"""

	def __init__(self):
		self.data = DataLoader(db=True)
		self.attractions = self.get_attractions()

	def get_attractions(self):
		"""
		Args:
			None
		Output:
			List of unique attractions
		"""
		self.data.link_attraction_park = self.data.load_file('link_attraction_park.csv')
		self.data.clean_link_attraction_park()
		return list(self.data.link_attraction_park.ATTRACTION.unique())

	def get_attendance(self, date: datetime.date):
		"""
		Args:
			df: DataFrame containing the forecasted attendance
			date: Date for which the attendance is requested
		Output:
			Forecasted attendance for the given date
		"""
		df = predict_attendance('prophet_model.pkl')
		output = df[df['ds'].dt.date.astype(str) == date]['yhat'].values[0]
		return int(str(int(output)).replace(',', ' '))

	def predicted_waiting_time(self, threshold_date: datetime.date, start_date: datetime.date, attractions=None, ):
		if attractions is None:
			attractions = self.attractions
		if 'Vertical Drop' in attractions:
			attractions.remove('Vertical Drop')
		self.data.predicted = self.data.load_file('lstm_attraction_wait_times.csv')
		self.data.predicted.DEB_TIME = pd.to_datetime(self.data.predicted.DEB_TIME)+ pd.Timedelta(days=365*3+1)
		self.data.predicted = self.data.predicted[['DEB_TIME', 'Source'] + attractions]
		hist = self.data.predicted[self.data.predicted['Source'] == 0]
		hist = hist[(hist['DEB_TIME'] <= threshold_date) & (hist['DEB_TIME'] >= start_date)]
		pred = self.data.predicted[self.data.predicted['Source'] == 1]
		max_pred = datetime.today() + timedelta(days=5)
		pred = pred[(pred['DEB_TIME'] >= threshold_date) & (pred['DEB_TIME'] <= max_pred)]
		return hist, pred

	def get_predicted_attendance_with_past(self, current_date: datetime.date, start_date: datetime.date):
		self.data.attendance = self.data.load_file('attendance.csv')
		self.data.clean_attendance()
		self.data.preprocess_attendance()
		hist = self.data.attendance.copy()
		hist['USAGE_DATE'] += timedelta(days=365*3+1)
		hist = hist[(hist['USAGE_DATE'] <= current_date) & (hist['USAGE_DATE'] >= start_date)].reset_index(drop=True)
		hist['predicted'] = 0

		pred = predict_attendance('prophet_model.pkl')
		pred.rename(columns={'ds': 'USAGE_DATE', 'yhat': 'attendance'}, inplace=True)
		pred['predicted'] = 1
		return hist, pred

	def compute_kpi1(self, attractions=None):
		"""
		Args:
			waiting_df: DataFrame containing the waiting times
			attractions: List of attractions to consider
		Output:
			count_percent: Percentage of time the waiting time was above the 80th percentile
		"""
		if attractions is None:
			attractions = self.attractions  # use all attractions if not specified
		self.data.waiting_times = self.data.load_file('fictional_waiting_times.csv')
		self.data.clean_waiting_times()
		waiting_df = self.data.waiting_times.copy()
		waiting_df = waiting_df[waiting_df['ENTITY_DESCRIPTION_SHORT'].isin(attractions)]
		wait_time_80 = waiting_df['WAIT_TIME_MAX'].quantile(0.8)
		count_sup_80 = waiting_df[(waiting_df['WAIT_TIME_MAX'] > wait_time_80) & (waiting_df['WAIT_TIME_MAX'] > 30)].shape[0]
		count_percent = str(round(count_sup_80 / waiting_df.shape[0] * 100, 2)) + '%'
		return count_percent

	def compute_kpi2(self, attractions=None):
		"""
		Args:
			merged_df: DataFrame containing the merged data of waiting times and attendance
			attractions: List of attractions to consider
		Output:
			WTEI_30_attrac: 30th percentile of the normalized waiting time for the attractions
			WTEI_70_attrac: 70th percentile of the normalized waiting time for the attractions
		"""
		if attractions is None:
			attractions = self.attractions
		self.data.waiting_times = self.data.load_file('lstm_attraction_wait_times.csv')
		df = self.data.waiting_times.copy()
		df['DEB_TIME'] = pd.to_datetime(df['DEB_TIME'])
		df = df[['DEB_TIME', 'Source'] + attractions]
		df = df[df['DEB_TIME'] >= datetime(2022, 2, 1)].sort_values(by='DEB_TIME').reset_index(drop=True)
		df_predicted = df[df['Source'] == 1].drop(columns=['Source'])
		df_actual = df[df['Source'] == 0].drop(columns=['Source'])

		for i in range(len(df_predicted.columns)):
			if df_predicted.columns[i] == 'DEB_TIME':
				continue
			df_actual[f'{df_predicted.columns[i]}_actual'] = df_actual[df_predicted.columns[i]]
			df_actual.drop(columns=[df_predicted.columns[i]], inplace=True)

		act_vs_pred = df_actual.merge(df_predicted, on='DEB_TIME', how='left')

		for i in range(len(df_predicted.columns)):
			if df_predicted.columns[i] == 'DEB_TIME':
				continue
			act_vs_pred[f'{df_predicted.columns[i]}_ratio'] = act_vs_pred[f'{df_predicted.columns[i]}_actual'] / act_vs_pred[df_predicted.columns[i]]
			act_vs_pred.drop(columns=[df_predicted.columns[i], f'{df_predicted.columns[i]}_actual'], inplace=True)

		act_vs_pred.drop(columns=['DEB_TIME'], inplace=True)
		WTEI_ratios =act_vs_pred.apply(lambda x: x[x != 0].mean(), axis=0).rename(index=lambda x: x.replace('_ratio', ''))
		return WTEI_ratios.to_dict()

	def compute_kpi3(self, attractions=None):
		"""
		Args:
			waiting_df: DataFrame containing the waiting times
			attractions: List of attractions to consider
		Output:
			benchmark_waiting_time_attrac: Average waiting time for the attractions of the past 30 days
		"""
		if attractions is None:
			attractions = self.attractions
		self.data.waiting_times = self.data.load_file('fictional_waiting_times.csv')
		self.data.clean_waiting_times()
		waiting_df = self.data.waiting_times.copy()
		max_date = datetime.today()
		date_minus_month = max_date - pd.DateOffset(months=1)
		restricted_waiting_time = waiting_df[(waiting_df['WORK_DATE'] >= date_minus_month) & (waiting_df['WORK_DATE'] <= max_date)]
		benchmark_waiting_time_attrac = restricted_waiting_time[restricted_waiting_time['ENTITY_DESCRIPTION_SHORT'].isin(attractions)]['WAIT_TIME_MAX'].mean()
		del waiting_df
		return benchmark_waiting_time_attrac
