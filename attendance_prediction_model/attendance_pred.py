# Imports
import pandas as pd
import numpy as np
from endless_line.data_utils.dataloader import DataLoader

# Import and clean the data
data = DataLoader(load_all_files=True)
df = data.clean_data()

# Display the first 5 rows of the data
print(df.head())