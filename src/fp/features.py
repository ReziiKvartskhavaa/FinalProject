from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List
import numpy as np
import pandas as pd

from fp.config import DEFAULT_CONFIG
from fp.io import read_csv, write_csv
from fp.tags import build_user_tag_cluster_percentages


# ---- Update these mappings to your real dictionaries ----
# If you already have dictionaries.py, you can import them instead.
ZONE_MAPPING: Dict[str, str] = {}  # optional
TAGS_TO_CLUSTER: Dict[str, str] = {
    # example keys -> clusters; replace with your real mapping
    "asian": "asian",
    "dessert": "dessert",
    "europian": "europian",
    "fast food": "fast food",
    "georgian": "georgian",
}

REQUIRED_ORDERS_COLS = [
    "User ID",
    "Order ID",
    "Provider ID",
    "Vendor ID",
    "Discount Type",
    "Is Refunded (Yes / No)",
    "Provider Price After Discount",
    "First Order Delivered Time",
    "is Order Delayed (Yes / No)",
    "Is Cash Dropoff (Yes / No)",
    "Average Order Full Time",
    "Courier Picked Up Time",
    "Estimated Time Minutes",
    "Discount Value Eur",
    "Price Before Discount Eur",
]

REQUIRED_ZONES_COLS = [
    "User ID",  # after rename
    "Order state",
    "Eater zone",
]

REQUIRED_TAGS_COLS = [
    "Provider ID",
    "Provider Tag",
    "Historical Average Rating",
]


def _resolve_path(path_or_name: str, data_dir: str | None) -> str:
    """
    If data_dir is provided and path_or_name is not an absolute path,
    treat it as relative to data_dir.
    """
    p = Path(path_or_name)
    if p.is_absolute() or data_dir is None:
        return str(p)
    return str(Path(data_dir) / path_or_name)


def _ensure_required(df: pd.DataFrame, cols: List[str], name: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing columns: {missing}")


def _parse_money_eur(series: pd.Series) -> pd.Series:
    # Handles "€12.30", "12,30", "12.30", "€1,234.56"
    s = series.astype(str).str.replace("€", "", regex=False).str.strip()
    # If comma appears as decimal separator like "12,30" and no dot exists -> swap comma to dot
    comma_decimal = s.str.contains(",") & ~s.str.contains(r"\.")
    s = s.where(~comma_decimal, s.str.replace(",", ".", regex=False))
    # Remove thousand separators: "1,234.56" -> "1234.56" (commas left now are thousand separators)
    s = s.str.replace(",", "", regex=False)
    return pd.to_numeric(s, errors="coerce")


def build_features(
    orders_path: str,
    zones_path: str,
    tags_path: str,
    out_path: str,
    data_dir: str | None = None,
    excluded_provider_ids: List[int] | None = None,
    min_orders_per_user: int | None = None,
) -> pd.DataFrame:
    excluded_provider_ids = excluded_provider_ids or DEFAULT_CONFIG.excluded_provider_ids
    min_orders_per_user = min_orders_per_user or DEFAULT_CONFIG.min_orders_per_user

    # Resolve paths (so CSVs can live outside project folder)
    orders_path = _resolve_path(orders_path, data_dir)
    zones_path = _resolve_path(zones_path, data_dir)
    tags_path = _resolve_path(tags_path, data_dir)

    tags = read_csv(tags_path)
    zones = read_csv(zones_path)
    orders = read_csv(orders_path, low_memory=True)

    # Align column name like your original script
    if "Orders Core Info & Metrics User ID" in zones.columns and "User ID" not in zones.columns:
        zones = zones.rename(columns={"Orders Core Info & Metrics User ID": "User ID"})

    _ensure_required(orders, REQUIRED_ORDERS_COLS, "orders")
    _ensure_required(zones, REQUIRED_ZONES_COLS, "zones")
    _ensure_required(tags, REQUIRED_TAGS_COLS, "tags")

    # Filter providers
    orders = orders[~orders["Provider ID"].isin(excluded_provider_ids)].copy()

    # Merge provider rating into orders (like you did)
    orders = orders.merge(tags[["Provider ID", "Historical Average Rating"]], on="Provider ID", how="left")

    # Clean money
    orders["Provider Price After Discount"] = _parse_money_eur(orders["Provider Price After Discount"])

    # Basic cleaning
    zones = zones.dropna(subset=["Eater zone"]).copy()
    tags = tags.dropna(subset=["Provider Tag"]).copy()

    # ---- Start building user-level main_data ----

    # Discount usage
    no_discount = orders.groupby("User ID").agg(
        No_Discount_Percentage=("Discount Type", lambda x: (x == "No Discount").mean() * 100.0)
    ).reset_index()
    no_discount["% of Targeted Campaigns"] = 100.0 - no_discount["No_Discount_Percentage"]
    main_data = no_discount.drop(columns=["No_Discount_Percentage"])

    # Core aggregates
    orders["First Order Delivered Time"] = pd.to_datetime(orders["First Order Delivered Time"], errors="coerce")
    grouped = orders.groupby("User ID").agg(
        Order_Count=("Order ID", "count"),
        Months_Since_Last_Order=("First Order Delivered Time", lambda x: (datetime.now() - x.max()).days / 30 if pd.notna(x.max()) else np.nan),
        Refund_Percentage=("Is Refunded (Yes / No)", lambda x: (x == "Yes").mean() * 100.0),
        Avg_Provider_Price=("Provider Price After Discount", "mean"),
    ).reset_index()
    main_data = main_data.merge(grouped, on="User ID", how="left")

    # Order delayed %
    delayed = orders.groupby(["User ID", "is Order Delayed (Yes / No)"]).size().reset_index(name="Count")
    pivot = delayed.pivot(index="User ID", columns="is Order Delayed (Yes / No)", values="Count").fillna(0)
    pivot["Total"] = pivot.sum(axis=1)
    pivot["order_late"] = np.where(pivot["Total"] > 0, (pivot.get("Yes", 0) / pivot["Total"]) * 100.0, 0.0)
    pivot["order_on_time"] = np.where(pivot["Total"] > 0, (pivot.get("No", 0) / pivot["Total"]) * 100.0, 0.0)
    pivot = pivot[["order_late", "order_on_time"]].reset_index()
    main_data = main_data.merge(pivot, on="User ID", how="left")

    # Pays with cash (1 if always cash)
    cash = orders.groupby(["User ID", "Is Cash Dropoff (Yes / No)"]).size().reset_index(name="Count")
    pivot_cash = cash.pivot(index="User ID", columns="Is Cash Dropoff (Yes / No)", values="Count").fillna(0)
    pivot_cash["Total"] = pivot_cash.sum(axis=1)
    pivot_cash["paysWithCash"] = np.where(pivot_cash["Total"] > 0, (pivot_cash.get("Yes", 0) == pivot_cash["Total"]).astype(int), 0)
    pivot_cash = pivot_cash[["paysWithCash"]].reset_index()
    main_data = main_data.merge(pivot_cash, on="User ID", how="left")

    # Failed order %
    state_counts = zones.groupby(["User ID", "Order state"]).size().unstack(fill_value=0).reset_index()
    if "" in state_counts.columns:
        state_counts = state_counts.rename(columns={"": "blank"})
    for col in ["blank", "ready_for_pickup", "rejected", "delivered", "failed"]:
        if col not in state_counts.columns:
            state_counts[col] = 0
    state_counts["total_orders"] = state_counts[["blank", "ready_for_pickup", "rejected", "delivered", "failed"]].sum(axis=1)
    state_counts["fail_percentage"] = np.where(state_counts["total_orders"] > 0, (state_counts["failed"] / state_counts["total_orders"]) * 100.0, 0.0)
    state_counts["fail_percentage"] = state_counts["fail_percentage"].fillna(0).round(2)
    main_data = main_data.merge(state_counts[["User ID", "fail_percentage"]], on="User ID", how="left")

    # Avg order full time
    avg_full_time = orders.groupby("User ID")["Average Order Full Time"].mean().reset_index()
    main_data = main_data.merge(avg_full_time, on="User ID", how="left")

    # Morning vs evening, Weekday vs weekend
    orders["Courier Picked Up Time"] = pd.to_datetime(orders["Courier Picked Up Time"], errors="coerce")

    def time_of_day(dt):
        if pd.isna(dt):
            return np.nan
        return "Morning" if 6 <= dt.hour < 16 else "Evening"

    def day_type(dt):
        if pd.isna(dt):
            return np.nan
        return "Weekday" if dt.weekday() < 5 else "Weekend"

    orders["Time of Day"] = orders["Courier Picked Up Time"].apply(time_of_day)
    tod = orders.groupby(["User ID", "Time of Day"]).size().reset_index(name="Count")
    tod_p = tod.pivot(index="User ID", columns="Time of Day", values="Count").fillna(0)
    tod_p["Total"] = tod_p.sum(axis=1)
    tod_p["Morning"] = np.where(tod_p["Total"] > 0, (tod_p.get("Morning", 0) / tod_p["Total"]) * 100.0, 0.0)
    tod_p["Evening"] = np.where(tod_p["Total"] > 0, (tod_p.get("Evening", 0) / tod_p["Total"]) * 100.0, 0.0)
    tod_p = tod_p[["Morning", "Evening"]].reset_index()
    main_data = main_data.merge(tod_p, on="User ID", how="left")

    orders["Day Type"] = orders["Courier Picked Up Time"].apply(day_type)
    dtc = orders.groupby(["User ID", "Day Type"]).size().reset_index(name="Count")
    dtc_p = dtc.pivot(index="User ID", columns="Day Type", values="Count").fillna(0)
    dtc_p["Total"] = dtc_p.sum(axis=1)
    dtc_p["Weekday"] = np.where(dtc_p["Total"] > 0, (dtc_p.get("Weekday", 0) / dtc_p["Total"]) * 100.0, 0.0)
    dtc_p["Weekend"] = np.where(dtc_p["Total"] > 0, (dtc_p.get("Weekend", 0) / dtc_p["Total"]) * 100.0, 0.0)
    dtc_p = dtc_p[["Weekday", "Weekend"]].reset_index()
    main_data = main_data.merge(dtc_p, on="User ID", how="left")

    # Provider tag cluster percentages
    tag_pct = build_user_tag_cluster_percentages(tags, orders, TAGS_TO_CLUSTER)
    main_data = main_data.merge(tag_pct, on="User ID", how="left")

    # Provider rating per user
    orders["Historical Average Rating"] = orders["Historical Average Rating"].fillna(0)
    pr = orders.groupby("User ID")["Historical Average Rating"].mean().reset_index()
    pr = pr.rename(columns={"Historical Average Rating": "Provider Rating"})
    main_data = main_data.merge(pr, on="User ID", how="left")

    # ETA per user
    eta = orders.groupby("User ID")["Estimated Time Minutes"].mean().reset_index()
    eta = eta.rename(columns={"Estimated Time Minutes": "ETA"})
    main_data = main_data.merge(eta, on="User ID", how="left")

    # GMV discount percentage (safe division)
    denom = pd.to_numeric(orders["Price Before Discount Eur"], errors="coerce")
    numer = pd.to_numeric(orders["Discount Value Eur"], errors="coerce")
    orders["Discount Percentage"] = np.where(denom > 0, (numer / denom) * 100.0, 0.0)
    gmv_disc = orders.groupby("User ID")["Discount Percentage"].mean().reset_index()
    gmv_disc = gmv_disc.rename(columns={"Discount Percentage": "GMV Discount Percentage"})
    main_data = main_data.merge(gmv_disc, on="User ID", how="left")
    main_data["GMV Discount Percentage"] = main_data["GMV Discount Percentage"].fillna(0)

    # Vendor concentration (top 3 vendors share)
    voc = orders.groupby(["User ID", "Vendor ID"]).agg(Vendor_Order_Count=("Order ID", "count")).reset_index()
    voc["Vendor_Rank"] = voc.groupby("User ID")["Vendor_Order_Count"].rank(method="first", ascending=False)
    top3 = voc[voc["Vendor_Rank"] <= 3]
    totals = orders.groupby("User ID")["Order ID"].count().rename("Total_Order_Count").reset_index()
    top3sum = top3.groupby("User ID")["Vendor_Order_Count"].sum().rename("Top_3_Order_Count").reset_index()
    vp = totals.merge(top3sum, on="User ID", how="left").fillna({"Top_3_Order_Count": 0})
    vp["Vendor Concentration"] = np.where(vp["Total_Order_Count"] > 0, (vp["Top_3_Order_Count"] / vp["Total_Order_Count"]) * 100.0, 0.0)
    main_data = main_data.merge(vp[["User ID", "Vendor Concentration"]], on="User ID", how="left")

    # Final cleaning / naming
    main_data = main_data.fillna(0)

    # Drop some columns (kept from your original logic)
    for col in ["Morning", "Weekday", "order_on_time"]:
        if col in main_data.columns:
            main_data = main_data.drop(columns=[col])

    # Remove invalid months (optional)
    main_data = main_data[main_data["Months_Since_Last_Order"] > 0]

    # Rename columns nicely (and FIXED your old rename bug)
    main_data = main_data.rename(columns={
        "Order_Count": "Order Count",
        "Months_Since_Last_Order": "Months Since Last Order",
        "Refund_Percentage": "Refund Percentage",
        "Avg_Provider_Price": "AOV",
    })

    # Apply min orders filter
    main_data["User ID"] = main_data["User ID"].astype(int)
    main_data = main_data[main_data["Order Count"] >= min_orders_per_user].copy()

    write_csv(main_data, out_path)
    return main_data