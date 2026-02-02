from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster

from fp.io import read_csv, write_csv, save_json


def cut_clusters(
    features_csv: str,
    linkage_npy: str,
    feature_cols: List[str],
    out_dir: str,
    cut_distance: Optional[float] = None,
    n_clusters: Optional[int] = None,
    max_rows: int | None = 40000,
) -> None:
    if (cut_distance is None) == (n_clusters is None):
        raise ValueError("Provide exactly one: cut_distance OR n_clusters")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    df = read_csv(features_csv)
    if max_rows is not None:
        df = df.iloc[:max_rows].copy()

    needed = ["User ID"] + feature_cols
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in features: {missing}")

    labels = df["User ID"].astype(int).tolist()
    X = df[feature_cols].fillna(0.0)

    Z = np.load(linkage_npy)

    if cut_distance is not None:
        clusters = fcluster(Z, t=float(cut_distance), criterion="distance")
        params = {"criterion": "distance", "cut_distance": float(cut_distance)}
    else:
        clusters = fcluster(Z, t=int(n_clusters), criterion="maxclust")
        params = {"criterion": "maxclust", "n_clusters": int(n_clusters)}

    clustered_users = pd.DataFrame({"User ID": labels, "Cluster": clusters})

    # cluster summary
    counts = clustered_users["Cluster"].value_counts().rename("Count")
    pct = clustered_users["Cluster"].value_counts(normalize=True).rename("Percentage") * 100.0
    summary = pd.DataFrame({"Cluster": counts.index, "Count": counts.values, "Percentage": pct.values})

    # merged for means
    merged = df[needed].merge(clustered_users, on="User ID", how="inner")
    means = merged.groupby("Cluster")[feature_cols].mean().reset_index()

    write_csv(clustered_users, out_path / "clustered_users.csv")
    write_csv(summary, out_path / "cluster_summary.csv")
    write_csv(means, out_path / "cluster_means.csv")

    save_json(
        {
            "features_csv": features_csv,
            "linkage_npy": linkage_npy,
            "feature_cols": feature_cols,
            **params,
            "max_rows": max_rows,
            "n_users": len(labels),
        },
        out_path / "run_meta.json",
    )
