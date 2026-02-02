from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import pandas as pd


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            params_json TEXT NOT NULL
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS user_features (
            run_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            features_json TEXT NOT NULL
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS clusters (
            run_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            cluster_id INTEGER NOT NULL
        )
        """)


def save_run(db_path: str, created_at: str, params: dict) -> int:
    with sqlite3.connect(db_path) as con:
        cur = con.execute(
            "INSERT INTO runs(created_at, params_json) VALUES (?, ?)",
            (created_at, json.dumps(params)),
        )
        return int(cur.lastrowid)


def save_features(db_path: str, run_id: int, features_df: pd.DataFrame) -> None:
    if "User ID" not in features_df.columns:
        raise ValueError("features_df must contain 'User ID'")
    with sqlite3.connect(db_path) as con:
        for _, row in features_df.iterrows():
            user_id = int(row["User ID"])
            features = row.drop(labels=["User ID"]).to_dict()
            con.execute(
                "INSERT INTO user_features(run_id, user_id, features_json) VALUES (?, ?, ?)",
                (run_id, user_id, json.dumps(features)),
            )


def save_clusters(db_path: str, run_id: int, clustered_users_df: pd.DataFrame) -> None:
    with sqlite3.connect(db_path) as con:
        for _, row in clustered_users_df.iterrows():
            con.execute(
                "INSERT INTO clusters(run_id, user_id, cluster_id) VALUES (?, ?, ?)",
                (run_id, int(row["User ID"]), int(row["Cluster"])),
            )
