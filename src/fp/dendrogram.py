from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram

from fp.io import read_csv


def plot_dendrogram(
    features_csv: str,
    linkage_npy: str,
    feature_cols: List[str],
    out_png: Optional[str] = None,
    truncate_p: int = 50,
    max_rows: int | None = 40000,
) -> str | None:
    df = read_csv(features_csv)

    if max_rows is not None:
        df = df.iloc[:max_rows].copy()

    needed = ["User ID"] + feature_cols
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    Z = np.load(linkage_npy)

    plt.figure(figsize=(12, 7))
    dendrogram(
        Z,
        truncate_mode="lastp",
        p=int(truncate_p),
        show_leaf_counts=True,
        no_labels=True,
    )
    plt.title("User Clustering Dendrogram")
    plt.xlabel("Clustered users")
    plt.ylabel("Euclidean distance")

    if out_png:
        out_path = Path(out_png)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(str(out_path), dpi=150)
        plt.close()
        return str(out_path)

    plt.show()
    return None
