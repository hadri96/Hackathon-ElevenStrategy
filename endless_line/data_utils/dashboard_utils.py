from endless_line.data_utils.dataloader import DataLoader
from datetime import datetime
class DashboardUtils:
	"""
	DashboardUtils class provides utility functions to interact with the data loaded by DataLoader.
  Methods
	-------
    def get_attractions(self):
        attraction_df = self.data.link_attraction_park
        return attraction_df['ATTRACTION'].values
    
    def get_attendance(self, df, date: datetime.date):
        output = df[df['ds'].dt.date.astype(str) == date]['yhat'].values[0]
        return int(str(int(output)).replace(',', ' '))
    
    def compute_kpi1(self, waiting_df, date=None):
        # KPI 1: Park performance on keeping customers loyal, see business notes
        wait_time_80 = waiting_df['WAIT_TIME_MAX'].quantile(0.8)
        count_sup_80 = waiting_df[waiting_df['WAIT_TIME_MAX'] > wait_time_80].shape[0]
        return str(round(count_sup_80/waiting_df.shape[0]*100, 2)) + '%'

    def compute_kpi2(self, waiting_df, date=None):
        # KPI 2: Park performance on improving waiting time, see business notes
        pass

    def compute_kpi3(self, waiting_df, date=None):
        # KPI 3: Park performance on managing customer flow, see business notes
        pass
        
	
	get_attractions() -> list:
		Returns a list of unique attractions
	"""

	def __init__(self):
		self.data = DataLoader(db=True)

	def get_attractions(self):
		self.data.link_attraction_park = self.data.load_file('link_attraction_park.csv')
		self.data.clean_link_attraction_park()
		return list(self.data.link_attraction_park.ATTRACTION.unique())

	def get_attendance(self, df, date: datetime.date):
		output = df[df['ds'].dt.date.astype(str) == date]['yhat'].values[0]
		return int(str(int(output)).replace(',', ' '))
