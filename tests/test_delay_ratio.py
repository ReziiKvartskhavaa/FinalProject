import pandas as pd
import numpy as np


def test_delay_ratio():
    df = pd.DataFrame({
        "User ID": [1,1,1,1],
        "is Order Delayed (Yes / No)": ["Yes","No","No","Yes"]
    })
    delayed = df.groupby(["User ID", "is Order Delayed (Yes / No)"]).size().reset_index(name="Count")
    pivot = delayed.pivot(index="User ID", columns="is Order Delayed (Yes / No)", values="Count").fillna(0)
    pivot["Total"] = pivot.sum(axis=1)
    late = (pivot.get("Yes", 0) / pivot["Total"]) * 100.0
    assert np.isclose(float(late.iloc[0]), 50.0)
