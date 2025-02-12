from endless_line.data_utils.dataloader import DataLoader

class DashboardUtils:
    """
    DashboardUtils class provides utility functions to interact with the data loaded by DataLoader.

    Methods
    -------
    get_attractions() -> list:
        Returns a list of unique attractions
    """

    def __init__(self, clean_data: bool = True):
        self.data = DataLoader(load_all_files=True, clean_data=clean_data)

    def get_attractions(self):
        return list(self.data.link_attraction_park.ATTRACTION.unique())
