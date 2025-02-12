import pickle
import os
from endless_line.data_utils.dashboard_utils import DataLoader

def save_model(model, filename, root_dir=DataLoader().root_dir):
	models_dir = os.path.join(root_dir, "models")
	filename = os.path.join(models_dir, filename)
	with open(filename, 'wb') as f:
		pickle.dump(model, f)

def load_model(filename, root_dir=DataLoader().root_dir):
    """Load the Prophet model from a file"""
    models_dir = os.path.join(root_dir, "models")
    filename = os.path.join(models_dir, filename)
    try:
        with open(filename, 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
