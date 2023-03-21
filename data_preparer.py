import data_reader
import data_vectorizer

import pandas as pd
import numpy as np
import tensorflow

vectorizers: list[data_vectorizer.Vectorizer] = None
def __get_vectorizers():
    global vectorizers
    if vectorizers is None:
        mapper = data_reader.get_mapper()
        vectorizers = list()
        for idx, row in mapper.iterrows():
            frames = data_reader.get_recon(row["h5"])
            timestamps = data_reader.get_timestamps(row["csv"])
            vectorizers.append(
                data_vectorizer.Vectorizer(frames, timestamps)
            )
    return vectorizers

def get_randomized_vectors(n_randomizations):
    vectorizers = __get_vectorizers()
    vectors = list()
    letters = list()
    for vectorizer in vectorizers:
        # print(vectorizer.timestamps)
        for _ in range(n_randomizations):
            sub_vectors, sub_letters = vectorizer.get_randomized_vectors()
            vectors.extend(sub_vectors)
            letters.extend(sub_letters)
    return vectors, letters

def get_default_vectors():
    vectorizers = __get_vectorizers()
    vectors = list()
    letters = list()
    for vectorizer in vectorizers:
        # print(vectorizer.timestamps)
        sub_vectors, sub_letters = vectorizer.get_randomized_vectors(0, 0)
        vectors.extend(sub_vectors)
        letters.extend(sub_letters)
    return vectors, letters

def get_max_frames():
    vectorizers = __get_vectorizers()
    length = 0
    for vectorizer in vectorizers:
        length = max(length, vectorizer.get_max_frames())
    return length

def get_all_letters():
    vectorizers = __get_vectorizers()
    letters = set()
    for vectorizer in vectorizers:
        letters.update(vectorizer.get_letters())
    return letters

def make_numpy(vectors, length: int):
    shape = (len(vectors), 7, 20, length)
    new_vectors = np.zeros(shape)
    for idx, vector in enumerate(vectors):
        new_vectors[idx, :, :, :vector.shape[-1]] = vector.copy()
        
    return np.reshape(new_vectors, (len(vectors), 7, 20*length))
    return new_vectors

