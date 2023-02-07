import numpy as np
import pandas as pd
import h5py
from pathlib import Path
from matplotlib import pyplot as plt
import math


rng = np.random.default_rng()

VECTOR_LENGTH = 20
VECTOR_COUNT = 7
vector_center_x = 70
vector_center_y = 85
vector_spacing_degrees = 30

class Data:
    def __init__(self, vector_mask: np.ndarray, base_image: np.ndarray) -> None:
        self.vector_mask = vector_mask
        self.base_image = base_image


    def plot_base_image_and_vectors(self, frame: int, vector_color="blue"):
        plt.imshow(self.base_image)
        

class Dataset:
    
    def __init__(self, data_path: Path) -> None:
        dataset = h5py.File(data_path, mode="r")
        self.data = dataset["recon"]
        
        
    def get_random_prepared_dataset(self):
        pass
    
    def get_randomized_vector_mask(self):
        vector_mask = np.ones((84, 84))
        center_x = self.__random_x(39, 39)
        center_y = self.__random_y(40, 43)
        rotation = self.__random_rotation(0, 0)
        vector_mask[center_x][center_y] = 0
        
        for i in range(VECTOR_COUNT):
            for j in range(VECTOR_LENGTH):
                x, y = self.__get_offsets(center_x, center_y, (rotation+25*i)+10, j)
                vector_mask[x][y] = 0
            
        return vector_mask

    
    def __get_offsets(self, center_x: int, center_y: int, rotation: float, distance: int):
        rad = math.radians(rotation)
        
        x = center_x - math.sin(rad) * distance
        y = center_y - math.cos(rad) * distance
        return round(x), round(y)
    
    def __random_x(self, min = 60, max = 70):
        return round(self.__random_value(min, max))
    
    def __random_y(self, min = 80, max = 90):
        return round(self.__random_value(min, max))
    
    def __random_rotation(self, min = -5, max = 5):
        return self.__random_value(min, max)
    
    def __random_value(self, min: int, max: int):
        delta = min - max
        random_val =  rng.random()
        random_val *= delta
        random_val -= min
        return random_val

