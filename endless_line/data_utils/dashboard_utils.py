from endless_line.data_utils.dataloader import DataLoader
from datetime import datetime
import pandas as pd


class DashboardUtils:
    """
    DashboardUtils class provides utility functions to interact with the data loaded by DataLoader.
    Methods
    -------
    get_attractions() -> list:
        Returns a list of unique attractions
    """

    def __init__(self):
        self.data = DataLoader(db=True)
        self.attractions = self.get_attractions()

    def get_attractions(self):
        self.data.link_attraction_park = self.data.load_file('link_attraction_park.csv')
        self.data.clean_link_attraction_park()
        return list(self.data.link_attraction_park.ATTRACTION.unique())

    def get_attendance(self, df, date: datetime.date):
        output = df[df['ds'].dt.date.astype(str) == date]['yhat'].values[0]
        return int(str(int(output)).replace(',', ' '))

    def compute_kpi1(self, waiting_df, attractions=None):
        if attractions is None:
            attractions = self.attractions  # use all attractions
        waiting_df = waiting_df[waiting_df['ENTITY_DESCRIPTION_SHORT'].isin(attractions)]
        wait_time_80 = waiting_df['WAIT_TIME_MAX'].quantile(0.8)
        count_sup_80 = waiting_df[waiting_df['WAIT_TIME_MAX'] > wait_time_80].shape[0]
        count_percent = str(round(count_sup_80 / waiting_df.shape[0] * 100, 2)) + '%'
        return count_percent

    def compute_kpi2(self, merged_df, attractions=None):
        if attractions is None:
            attractions = self.attractions
        wait_time_30_attrac = merged_df[merged_df['ATTRACTION'].isin(attractions)]['wait_time_normalized'].quantile(0.30)    
        wait_time_70_attrac = merged_df[merged_df['ATTRACTION'].isin(attractions)]['wait_time_normalized'].quantile(0.70)
        return wait_time_30_attrac, wait_time_70_attrac

    def compute_kpi3(self, waiting_df, attractions=None):
        if attractions is None:
            attractions = self.attractions
        max_date = waiting_df['WORK_DATE'].max()
        date_minus_month = max_date - pd.DateOffset(months=1)
        restricted_waiting_time = waiting_df[(waiting_df['WORK_DATE'] >= date_minus_month) & (waiting_df['WORK_DATE'] <= max_date)]
        benchmark_waiting_time_attrac = restricted_waiting_time[restricted_waiting_time['ENTITY_DESCRIPTION_SHORT'].isin(attractions)]['WAIT_TIME_MAX'].mean()
        return benchmark_waiting_time_attrac
