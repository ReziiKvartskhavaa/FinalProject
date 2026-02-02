from __future__ import annotations

import time
from pathlib import Path
import streamlit as st
import pandas as pd

from fp.linkage import compute_linkage
from fp.cluster import cut_clusters
from fp.report import generate_report
from fp.dendrogram import plot_dendrogram


st.set_page_config(page_title="FP Clustering UI", layout="wide")

st.title("Final Project — Clustering UI")
st.caption("Pick columns → run linkage → dendrogram → cluster → report")

# ---- Inputs ---- PYTHONPATH=src streamlit run app.py
features_csv = st.text_input("Features CSV path", value="artifacts/features.csv")

col1, col2, col3 = st.columns(3)
with col1:
    max_rows = st.number_input("Max rows (speed)", min_value=1000, max_value=200000, value=40000, step=1000)
with col2:
    truncate_p = st.number_input("Dendrogram truncate p", min_value=10, max_value=200, value=50, step=5)
with col3:
    run_name = st.text_input("Run name (folder)", value=f"run_ui_{int(time.time())}")

out_dir = Path("artifacts") / run_name
out_dir.mkdir(parents=True, exist_ok=True)

# ---- Load features + choose columns ----
if not Path(features_csv).exists():
    st.error(f"Features file not found: {features_csv}")
    st.stop()

df = pd.read_csv(features_csv)
st.write(f"Loaded features: **{df.shape[0]:,}** users × **{df.shape[1]}** columns")

numeric_cols = [c for c in df.columns if c != "User ID" and pd.api.types.is_numeric_dtype(df[c])]
default_pick = [c for c in ["ETA", "Provider Rating", "GMV Discount Percentage", "Vendor Concentration", "AOV"] if c in numeric_cols]
feature_cols = st.multiselect("Choose numeric columns for clustering", options=numeric_cols, default=default_pick)

st.divider()

# ---- Clustering controls ----
mode = st.radio("How to cut clusters?", ["Cut distance", "Number of clusters"], horizontal=True)
cut_distance = None
n_clusters = None
if mode == "Cut distance":
    cut_distance = st.slider("cut-distance", min_value=1.0, max_value=50.0, value=12.0, step=0.5)
else:
    n_clusters = st.slider("n-clusters", min_value=2, max_value=50, value=8, step=1)

st.divider()

# ---- Run pipeline ----
run_button = st.button("🚀 Run clustering", type="primary", disabled=(len(feature_cols) < 2))

if run_button:
    if len(feature_cols) < 2:
        st.error("Pick at least 2 columns.")
        st.stop()

    linkage_path = out_dir / "linkage.npy"
    linkage_meta = out_dir / "linkage_meta.json"
    dendro_path = out_dir / "dendrogram.png"
    report_path = out_dir / "report.md"

    with st.status("Running pipeline…", expanded=True) as status:
        st.write("1) Computing linkage…")
        compute_linkage(
            features_csv=features_csv,
            feature_cols=feature_cols,
            out_npy=str(linkage_path),
            meta_json=str(linkage_meta),
            method="ward",
            scale=True,
            max_rows=int(max_rows),
        )

        st.write("2) Saving dendrogram…")
        plot_dendrogram(
            features_csv=features_csv,
            linkage_npy=str(linkage_path),
            feature_cols=feature_cols,
            out_png=str(dendro_path),
            truncate_p=int(truncate_p),
            max_rows=int(max_rows),
        )

        st.write("3) Cutting clusters…")
        cut_clusters(
            features_csv=features_csv,
            linkage_npy=str(linkage_path),
            feature_cols=feature_cols,
            out_dir=str(out_dir),
            cut_distance=float(cut_distance) if cut_distance is not None else None,
            n_clusters=int(n_clusters) if n_clusters is not None else None,
            max_rows=int(max_rows),
        )

        st.write("4) Generating report…")
        generate_report(run_dir=str(out_dir), out_path=str(report_path))

        status.update(label="✅ Done", state="complete", expanded=False)

    st.success(f"Saved run outputs to: {out_dir}")

# ---- Show outputs if present ----
summary_csv = out_dir / "cluster_summary.csv"
means_csv = out_dir / "cluster_means.csv"
report_md = out_dir / "report.md"
dendro_png = out_dir / "dendrogram.png"

left, right = st.columns([1, 1])

with left:
    st.subheader("Dendrogram")
    if dendro_png.exists():
        st.image(str(dendro_png), use_container_width=True)
    else:
        st.info("Run clustering to generate dendrogram.")

with right:
    st.subheader("Cluster Summary")
    if summary_csv.exists():
        summary = pd.read_csv(summary_csv)
        st.dataframe(summary, use_container_width=True)
    else:
        st.info("Run clustering to generate cluster summary.")

st.subheader("Cluster Means")
if means_csv.exists():
    means = pd.read_csv(means_csv)
    st.dataframe(means, use_container_width=True)
else:
    st.info("Run clustering to generate cluster means.")

st.subheader("Report")
if report_md.exists():
    st.markdown(Path(report_md).read_text(encoding="utf-8"))
else:
    st.info("Run clustering to generate report.")
