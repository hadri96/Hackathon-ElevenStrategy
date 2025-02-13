from endless_line.data_utils.dataloader import DataLoader
from attendance_prediction_model.new_attedance_pred import predict_attendance
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

    def get_attendance(self, df, date: datetime.date):
        """
        Args:
            df: DataFrame containing the forecasted attendance
            date: Date for which the attendance is requested
        Output:
            Forecasted attendance for the given date
        """
        output = df[df['ds'].dt.date.astype(str) == date]['yhat'].values[0]
        return int(str(int(output)).replace(',', ' '))

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

    def compute_kpi1(self, waiting_df, attractions=None):
        """
        Args:
            waiting_df: DataFrame containing the waiting times
            attractions: List of attractions to consider
        Output:
            count_percent: Percentage of time the waiting time was above the 80th percentile
        """
        if attractions is None:
            attractions = self.attractions  # use all attractions if not specified
        waiting_df = waiting_df[waiting_df['ENTITY_DESCRIPTION_SHORT'].isin(attractions)]
        wait_time_80 = waiting_df['WAIT_TIME_MAX'].quantile(0.8)
        count_sup_80 = waiting_df[waiting_df['WAIT_TIME_MAX'] > wait_time_80].shape[0]
        count_percent = str(round(count_sup_80 / waiting_df.shape[0] * 100, 2)) + '%'
        return count_percent

    def compute_kpi2(self, merged_df, attractions=None):
        """
        Args:
            merged_df: DataFrame containing the merged data of waiting times and attendance
            attractions: List of attractions to consider
        Output:
            wait_time_30_attrac: 30th percentile of the normalized waiting time for the attractions
            wait_time_70_attrac: 70th percentile of the normalized waiting time for the attractions
        """
        if attractions is None:
            attractions = self.attractions
        wait_time_30_attrac = merged_df[merged_df['ATTRACTION'].isin(attractions)]['wait_time_normalized'].quantile(0.30)    
        wait_time_70_attrac = merged_df[merged_df['ATTRACTION'].isin(attractions)]['wait_time_normalized'].quantile(0.70)
        return (wait_time_30_attrac, wait_time_70_attrac)

    def compute_kpi3(self, waiting_df, attractions=None):
        """
        Args:
            waiting_df: DataFrame containing the waiting times
            attractions: List of attractions to consider
        Output:
            benchmark_waiting_time_attrac: Average waiting time for the attractions of the past 30 days
        """
        if attractions is None:
            attractions = self.attractions
        max_date = waiting_df['WORK_DATE'].max()
        date_minus_month = max_date - pd.DateOffset(months=1)
        restricted_waiting_time = waiting_df[(waiting_df['WORK_DATE'] >= date_minus_month) & (waiting_df['WORK_DATE'] <= max_date)]
        benchmark_waiting_time_attrac = restricted_waiting_time[restricted_waiting_time['ENTITY_DESCRIPTION_SHORT'].isin(attractions)]['WAIT_TIME_MAX'].mean()
        return benchmark_waiting_time_attrac
