from __future__ import annotations
from pathlib import Path
import json
import pandas as pd


def read_csv(path: str | Path, low_memory: bool = False) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=low_memory)


def write_csv(df: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_json(obj: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
