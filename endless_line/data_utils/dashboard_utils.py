from endless_line.data_utils.dataloader import DataLoader
from datetime import datetime

class DashboardUtils:
    """
    DashboardUtils class provides utility functions to interact with the data loaded by DataLoader.

    Methods
    -------
    get_attractions() -> list:
        Returns a list of unique attractions
    """

    def __init__(self, clean_data: bool = True):
        # self.data = DataLoader(load_all_files=True, clean_data=clean_data)
        self.data = DataLoader(load_all_files=True)
        if clean_data:
            self.data.clean_data()

    def get_attractions(self):
        attraction_df = self.data.link_attraction_park
        return attraction_df['ATTRACTION'].values
    
    def get_attendance(self, df, date: datetime.date):
        output = df[df['ds'].dt.date.astype(str) == date]['yhat'].values[0]
        return int(str(int(output)).replace(',', ' '))

        
    


