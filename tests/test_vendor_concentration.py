import pandas as pd
import numpy as np


def test_vendor_concentration_top3_share():
    orders = pd.DataFrame({
        "User ID": [1]*10,
        "Vendor ID": [10]*5 + [11]*3 + [12]*1 + [13]*1,
        "Order ID": list(range(10)),
    })
    voc = orders.groupby(["User ID", "Vendor ID"]).agg(Vendor_Order_Count=("Order ID", "count")).reset_index()
    voc["Vendor_Rank"] = voc.groupby("User ID")["Vendor_Order_Count"].rank(method="first", ascending=False)
    top3 = voc[voc["Vendor_Rank"] <= 3]
    total = orders.groupby("User ID")["Order ID"].count().iloc[0]
    top3sum = top3["Vendor_Order_Count"].sum()
    conc = (top3sum / total) * 100.0
    assert np.isclose(conc, 90.0)
