from __future__ import annotations

from typing import List
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage
from sklearn.preprocessing import StandardScaler

from fp.io import read_csv, save_json


def compute_linkage(
    features_csv: str,
    feature_cols: List[str],
    out_npy: str,
    meta_json: str | None = None,
    method: str = "ward",
    scale: bool = True,
    max_rows: int | None = 40000,
) -> np.ndarray:
    df = read_csv(features_csv)

    if max_rows is not None:
        df = df.iloc[:max_rows].copy()

    needed = ["User ID"] + feature_cols
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in features: {missing}")

    X = df[feature_cols].copy()
    X = X.fillna(0.0)

    if scale:
        scaler = StandardScaler()
        Xv = scaler.fit_transform(X.values)
    else:
        Xv = X.values

    Z = linkage(Xv, method=method)
    np.save(out_npy, Z)

    if meta_json:
        save_json(
            {
                "features_csv": features_csv,
                "feature_cols": feature_cols,
                "method": method,
                "scale": scale,
                "max_rows": max_rows,
            },
            meta_json,
        )

    return Z
