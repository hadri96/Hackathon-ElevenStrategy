from endless_line.data_utils.dataloader import DataLoader
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
from endless_line.data_utils.dataloader import DataLoader

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
