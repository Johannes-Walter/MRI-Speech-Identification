import pandas as pd
import numpy as np
import pandas as pd
import h5py
from pathlib import Path
from matplotlib import pyplot as plt
import math
import cv2

# Settings

datafile = "sub001_2drt_01_vcv1_r1_recon.h5"

timestamps_file = Path("Timestamps.csv")

# More Settings

VECTOR_LENGTH = 20
VECTOR_COUNT = 7
FRAMEREATE = 83.28  # Vielleicht sollte hier 50 rein?    
#                     # Das passt mehr oder weniger
#                     # Steht aber auch nirgends
# FRAMEREATE = 55.18   # Mathematik sagt 55 FPS, da das MP4-Matsch ist

vector_center_x = 39
vector_center_y = 40
vector_spacing_degrees = 30

# Here's the code



def get_vector_positions() -> list[list[int, int]]:
    vectors = np.zeros((VECTOR_COUNT, 2, VECTOR_LENGTH), dtype=np.intp)

    center_x = vector_center_x
    center_y = vector_center_y
    rotation = 0

    for i, vector in enumerate(vectors):
        for j in range(VECTOR_LENGTH):
            x, y = __get_offsets(center_x, center_y, (rotation+25*i)+10, j)
            vector[0][j] = x
            vector[1][j] = y

    return vectors
        

def get_vector_mask():
    vector_mask = np.ones((84, 84))

    vectors = get_vector_positions()


    for vector in vectors:
        vector_mask[vector[0], np.array(vector[1], dtype=np.intp)] = 0
    
    
    return vector_mask


def __get_offsets(center_x: int, center_y: int, rotation: float, distance: int):
    rad = math.radians(rotation)
    
    x = center_x - math.sin(rad) * distance
    y = center_y - math.cos(rad) * distance
    return round(x), round(y)

def add_frame_numbers(df: pd.DataFrame):

    df["Timestamp start"] = pd.to_timedelta(df["Timestamp start"])
    df["first_frame"] = df["Timestamp start"].dt.total_seconds() * FRAMEREATE

    df["Timestamp ende"] = pd.to_timedelta(df["Timestamp ende"])
    df["last_frame"] = df["Timestamp ende"].dt.total_seconds() * FRAMEREATE

    return df

def plot_video(dataset: np.ndarray, savefile: Path):
    # codec = cv2.VideoWriter_fourcc(*"mp4V")
    codec = cv2.VideoWriter_fourcc(*"avc1")
    frames, width, height = np.shape(dataset)

    out = cv2.VideoWriter(str(savefile), codec, FRAMEREATE, (width, height))

    for idx, frame in enumerate(dataset):
        print(f"Frame {idx}")
        frame = np.rot90(frame, k=3)
        frame = np.flip(frame, axis=1)

        frame = np.interp(frame, (frame.min(), frame.max()), (0, 255))

        frame = np.int16(frame)
        
        # frame = cv2.medianBlur(frame, 3)
        # frame = cv2.equalizeHist(frame)

        frame = np.stack([frame]*3, axis=-1)
        out.write(frame.astype(np.uint8))
    
    out.release()
    

def plot_frames(dataset: np.ndarray, savefolder: Path):
    fig = plt.figure()
    savefolder.mkdir(exist_ok=True)
    for idx, frame in enumerate(dataset):

        frame = np.rot90(frame, k=3)
        frame = np.flip(frame, axis=1)

        plt.imshow(frame, cmap="Greys_r")
        print(savefolder / f"frame_{idx}.png")
        plt.savefig(savefolder / f"frame_{idx}.png")
        plt.clf()

if __name__ == "__main__":
    patient_folder = "sub001"

    # datafile = "sub001_2drt_01_vcv1_r1_raw.h5"
    # filepath = Path("data", patient_folder, "2drt", "raw", datafile)

    datafile = "sub001_2drt_01_vcv1_r1_recon.h5"
    filepath = Path("data", patient_folder, "2drt", "recon", datafile)

    dataset = h5py.File(filepath)
    dset = dataset["recon"][:]

    # dset = dset[::-1]


    # # Retrieve and rotate the image
    # img = dataset["recon"][0]
    # img = np.rot90(img, k=3)
    # img = np.flip(img, axis=1)

    # mask = get_vector_mask()
    # ma = np.ma.MaskedArray(mask, mask)
    # plt.imshow(img, "Greys_r")
    # plt.imshow(ma, "winter_r")
    # plt.show()

    df = pd.read_csv(timestamps_file, sep=";")
    df = add_frame_numbers(df)
    # print(df)

    print(len(dataset["recon"]))
    savepath = Path("output")
    for idx, row in df.iterrows():
        print(f"Saving {idx}")
        first_frame = int(row["first_frame"])
        last_frame = int(row["last_frame"])
        # dset = dataset["recon"]#[first_frame:last_frame]#[::10]
        # dset = dset[::-1]
        print("gif...")
        plot_video(dset, savepath / f"video_{idx}.mp4")
        print("images...")
        # plot_frames(dset, savepath / f"{idx}")
        print()
        break
    # print(dataset.keys())
    # print(dataset["dataset"]["data"][:])