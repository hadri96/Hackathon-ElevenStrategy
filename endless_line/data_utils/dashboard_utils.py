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

    def compute_kpi1(self, waiting_df):
        # KPI 1: Park performance on keeping customers loyal, see business notes
        kpis_attrac = {}
        for attrac in self.get_attractions():
            temp_df = waiting_df[waiting_df['ENTITY_DESCRIPTION_SHORT']==attrac]
            wait_time_80 = temp_df['WAIT_TIME_MAX'].quantile(0.8)
            count_sup_80 = temp_df[temp_df['WAIT_TIME_MAX'] > wait_time_80].shape[0]
            count_percent = str(round(count_sup_80/temp_df.shape[0]*100, 2)) + '%'
            kpis_attrac[attrac] = count_percent
        wait_time_80 = waiting_df['WAIT_TIME_MAX'].quantile(0.8)
        count_sup_80 = waiting_df[waiting_df['WAIT_TIME_MAX'] > wait_time_80].shape[0]
        count_percent = str(round(count_sup_80/waiting_df.shape[0]*100, 2)) + '%'
        kpis_attrac['Global'] = count_percent
        return kpis_attrac

    def compute_kpi2(self, merged_df):
        """
        data = DataLoader(load_all_files=True)
        data.clean_data()
        attendance = data.attendance
        waiting_time = data.waiting_times
        merged = pd.merge(attendance, waiting_time, left_on=['USAGE_DATE'], right_on=['WORK_DATE'], how='right').drop(columns=['USAGE_DATE', 'FACILITY_NAME']).dropna(subset=['attendance'])
        merged['wait_time_normalized'] = merged['WAIT_TIME_MAX'] / 14*4 # assumption : open from 8 to 22 --> 14hours, with 4 periods of 15min per hour
        """
        # KPI 2: Park performance on improving waiting time, see business notes
        kpis_attrac = {}
        for attrac in self.get_attractions():
            wait_time_30_attrac = merged_df[merged_df['ATTRACTION'] == attrac]['wait_time_normalized'].quantile(0.30)
            wait_time_70_attrac = merged_df[merged_df['ATTRACTION'] == attrac]['wait_time_normalized'].quantile(0.70)
            kpis_attrac[attrac] = (wait_time_30_attrac, wait_time_70_attrac)
        kpis_attrac['Global'] = (merged_df['wait_time_normalized'].quantile(0.30), merged_df['wait_time_normalized'].quantile(0.70))
        return kpis_attrac

    def compute_kpi3(self, waiting_df):
        # KPI 3: Park waiting time tracking for customers, see business notes
        max_date = waiting_df['WORK_DATE'].max()
        date_minus_month = max_date - pd.DateOffset(months=1)
        restricted_waiting_time = waiting_df[(waiting_df['WORK_DATE'] >= date_minus_month) & (waiting_df['WORK_DATE'] <= max_date)]
        kpis_attrac = {}
        for attrac in self.get_attractions():
            benchmark_waiting_time_attrac = restricted_waiting_time[restricted_waiting_time['ENTITY_DESCRIPTION_SHORT']==attrac]['WAIT_TIME_MAX'].mean()
            kpis_attrac[attrac] = benchmark_waiting_time_attrac
        kpis_attrac['Global'] = restricted_waiting_time['WAIT_TIME_MAX'].mean()
        return kpis_attrac
