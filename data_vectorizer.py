

import numpy as np
import math
import pandas as pd
import torch

class Vectorizer:
    VECTOR_LENGTH = 20
    VECTOR_COUNT = 7

    VECTOR_SPAN_DEGREES = 180
    ROTATION_OFFSET_DEGREES = 180

    X_OFFSET = 40
    Y_OFFSET = 40

    IMAGE_SIZE = 84

    frames: np.array
    timestamps: pd.DataFrame
    rng: np.random.Generator


    def __init__(self, frames: np.array, timestamps: pd.DataFrame) -> None:
        self.frames = frames
        self.timestamps = timestamps

        self.rng = np.random.default_rng()
    

    def get_randomized_vectors(self, max_offset = 4, max_rotation = 10):
        relative = self.__get_vectors_relative_position(max_rotation)
        absolute = self.__get_vectors_absolute_position(relative, max_offset)

        vectors = list()
        letters = list()
        for idx, row in self.timestamps.iterrows():
            vectors.append(
                self.__get_pixel_data(
                    absolute,
                    int(row["first_frame"]),
                    int(row["last_frame"])
                ))
            letters.append(row["Buchstabe"])

        return vectors, letters


    def __get_pixel_data(self, vector_positions: np.array, first_frame: int, last_frame: int):
        total_frames = last_frame - first_frame
        frames = self.frames[first_frame:last_frame]

        vector_count = self.VECTOR_COUNT
        vector_length = self.VECTOR_LENGTH

        vectors = np.ones((vector_count, total_frames, vector_length))
        for vector_coords, image in zip(vector_positions, vectors):
            for col, frame in zip(image, frames):
                xs = [coords[0] for coords in vector_coords]
                ys = [coords[1] for coords in vector_coords]
                col[:] = frame[xs, ys]

        vectors = np.rot90(vectors, axes=(1, 2))
        return vectors


    def __get_mask(self, vectors_absolute_position):
        vector_mask = np.ones((self.IMAGE_SIZE, self.IMAGE_SIZE))
        for vector in vectors_absolute_position:
            for x, y in vector:
                vector_mask[x, y] = 0
    
        # return np.ma.MaskedArray(vector_mask, vector_mask)
        return vector_mask
    

    def __get_vectors_absolute_position(self, realative_vector_positions: np.ndarray, max_offset):
        vectors = realative_vector_positions.copy()
        vectors[...,1] += int(self.X_OFFSET - self.rng.random() * 2*max_offset - max_offset)
        vectors[...,0] += int(self.Y_OFFSET - self.rng.random() * 2*max_offset - max_offset)
        return vectors


    def __get_vectors_relative_position(self, max_rotation):

        vector_count = self.VECTOR_COUNT
        vector_length = self.VECTOR_LENGTH
        vector_span_degrees = self.VECTOR_SPAN_DEGREES

        rotation_offset_degrees = self.ROTATION_OFFSET_DEGREES + self.rng.random() * 2*max_rotation - max_rotation

        vector_spacing_degrees = vector_span_degrees / (vector_count - 1)
        vectors = np.zeros((vector_count, vector_length, 2), dtype=np.intp)

        for i, vector in enumerate(vectors):
            for j in range(vector_length):
                rotation = vector_spacing_degrees*i+self.ROTATION_OFFSET_DEGREES+rotation_offset_degrees

                x, y = self.__get_offsets(rotation, j)
                vector[j][0] = x
                vector[j][1] = y

        return vectors
    

    @staticmethod
    def __get_offsets(rotation: float, distance: int):
        rad = math.radians(rotation)
        
        x = math.sin(rad) * distance
        y = math.cos(rad) * distance
        return round(x), round(y)
    
    def get_max_frames(self):
        length = self.timestamps["last_frame"] - self.timestamps["first_frame"]
        return int(length.max())
    
    def get_letters(self):
        return set(self.timestamps["Buchstabe"])