import pandas as pd
import h5py
from pathlib import Path
import numpy as np

BASE_FOLDER = Path("data", "sub001")

FRAME_RATE = 83.28
FRAME_DURATION = 1/FRAME_RATE


def get_mapper(mapper_file: Path = None) -> pd.DataFrame:
    if mapper_file is None:
        mapper_file = BASE_FOLDER / "timestamps" / "mapper.csv"
    
    mapper = pd.read_csv(mapper_file)
    return mapper


def get_timestamps(filename: Path):
    filepath = BASE_FOLDER / "timestamps" / filename
    df = __read_timestamps(filepath)
    df = __clean_timestamps(df)
    return df


def __read_timestamps(filepath: Path):

    if filepath.suffix == ".csv":
        dtypes = {
            "Buchstabe": str,
            "Buchstabennr": int,
            "Timestamp start": str,
            "Timestamp ende": str,
        }
        df = pd.read_csv(filepath, sep=";",
                         dtype=dtypes)
    elif filepath.suffix == ".xlsx":
        def format(num: float):
            return f"{num/1000:.3f}"
        df = pd.read_excel(filepath,
                           converters={2: format, 3: format})
        df = df.rename({
            "start": "Timestamp start",
            "ende": "Timestamp ende",
            "Start": "Timestamp start",
            "Ende": "Timestamp ende",
        }, axis="columns")
    else:
        raise TypeError(f"Suffix not supported: {filepath.suffix}")
    
    return df


def __clean_timestamps(df: pd.DataFrame):

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


def get_recon(filename: Path):
    filepath = BASE_FOLDER / "2drt" / "recon" / filename
    recon = h5py.File(filepath)["recon"][:]
    recon = np.rot90(recon, k=3, axes=(1,2))
    recon = np.flip(recon, axis=2)
    return recon