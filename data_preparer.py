import numpy as np
import pandas as pd
import h5py
from pathlib import Path

rng = np.random.default_rng()

class Dataset:
    
    def __init__(self, data_path: Path) -> None:
        dataset = h5py.File(data_path, mode="r")
        self.data = h5py["recon"]
        
    def get_random_prepared_dataset(self):
        pass
    
    def __random_selection(self, min_x = 20, min_y = 20, max_x = 100):
        """genera
        """
    
    def __random_rotation(self):
        pass