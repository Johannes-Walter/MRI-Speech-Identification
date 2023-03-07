import h5py
import numpy as np
import pandas as pd
from pathlib import Path
import math

###############################################
# Some Constants

VECTOR_LENGTH = 20
VECTOR_COUNT = 7
FRAME_RATE = 83.28
FRAME_DURATION = 1/FRAME_RATE

VECTOR_SPAN_DEGREES = 180
ROTATION_OFFSET_DEGREES = 180

X_OFFSET = 40
Y_OFFSET = 40

IMAGE_SIZE = 84


###############################################
# Code


def get_recon(filepath: Path):
    recon = h5py.File(filepath)["recon"][:]
    recon = np.rot90(recon, k=3, axes=(1,2))
    recon = np.flip(recon, axis=2)
    return recon


def get_vectors_relative_position(vector_count: int, vector_span_degrees: float, vector_length: int, rotation_offset_degrees: float = 0):
    vector_spacing_degrees = vector_span_degrees / (vector_count - 1)
    print(f"Spacing: {vector_spacing_degrees} degrees")
    vectors = np.zeros((vector_count, vector_length, 2), dtype=np.intp)

    for i, vector in enumerate(vectors):
        for j in range(vector_length):
            rotation = vector_spacing_degrees*i+ROTATION_OFFSET_DEGREES+rotation_offset_degrees

            x, y = __get_offsets(rotation, j)
            vector[j][0] = x
            vector[j][1] = y

    return vectors

def __get_offsets(rotation: float, distance: int):
    rad = math.radians(rotation)
    
    x = math.sin(rad) * distance
    y = math.cos(rad) * distance
    return round(x), round(y)

def get_vectors_absolute_position(realative_vector_positions: np.ndarray, offset_x = 0, offset_y = 0):
    vectors = realative_vector_positions.copy()
    vectors[...,1] += X_OFFSET - offset_x
    vectors[...,0] += Y_OFFSET - offset_y
    return vectors

def get_mask(vectors_absolute_position):
    vector_mask = np.ones((IMAGE_SIZE, IMAGE_SIZE))
    for vector in vectors_absolute_position:
        for x, y in vector:
            vector_mask[x, y] = 0
    
    # return np.ma.MaskedArray(vector_mask, vector_mask)
    return vector_mask
    
def read_timestamps(filepath: Path):
    dtypes = {
        "Buchstabe": str,
        "Buchstabennr": int,
        "Timestamp start": str,
        "Timestamp ende": str,
    }
    df = pd.read_csv(filepath, sep=";", dtype=dtypes)

    # Die Spalten in den Zeitangaben müssen in dem Format "HH;MM:SS.SSSS" sein
    # Da wir nur Sekunden verwenden wird der Rest mit "00:" aufgefüllt
    # Kann zu Problemen führen falls wir 1-Minuten-Lange Videos haben, dann muss nach ":" gesucht werden
    for _ in range(2):
        idx = ~df["Timestamp start"].str.startswith("00:00:")
        df.loc[idx, "Timestamp start"] = "00:" + df[idx]["Timestamp start"].astype(str)

        idx = ~df["Timestamp ende"].str.startswith("00:00:")
        df.loc[idx, "Timestamp ende"] = "00:" + df[idx]["Timestamp ende"].astype(str)
    
    df["Timestamp start"] = pd.to_timedelta(df["Timestamp start"])
    df["Timestamp ende"] = pd.to_timedelta(df["Timestamp ende"])

    df["first_frame"] = df["Timestamp start"].dt.total_seconds() // FRAME_DURATION
    df["last_frame"] = df["Timestamp ende"].dt.total_seconds() // FRAME_DURATION
    return df


def get_pixel_data(recon: np.ndarray, vectors_absolute_position: np.ndarray, timestamps: pd.Series):
    first_frame = round(timestamps["first_frame"])
    last_frame = round(timestamps["last_frame"])
    total_frames = last_frame - first_frame

    vector_count = vectors_absolute_position.shape[0]
    vector_length = vectors_absolute_position.shape[1]

    vectors = np.ones((vector_count, total_frames, vector_length))
    for vector_coords, image in zip(vectors_absolute_position, vectors):
        for col, frame in zip(image, recon[first_frame:last_frame]):
            xs = [coords[0] for coords in vector_coords]
            ys = [coords[1] for coords in vector_coords]
            col[:] = frame[xs, ys]

    vectors = np.rot90(vectors, axes=(1, 2))
    return vectors

if __name__ == "__main__":
    file = Path("data", "sub001", "timestamps", "sub001_2drt_01_vcv1_r1_recon.csv")
    f = read_timestamps(file)
    print(f)


