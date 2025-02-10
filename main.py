from endless_line.data_utils.dataloader import DataLoader

if __name__ == "__main__":
    dataloader = DataLoader()
    data = dataloader.load_data(".csv")
    print(data)
