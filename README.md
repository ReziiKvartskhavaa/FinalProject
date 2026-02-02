# Final Project — User Segmentation (Food Delivery)

This project builds user-level features from raw order/zones/provider-tag exports and performs hierarchical clustering
(Ward linkage). It outputs clustered users + summaries + a markdown report.

## Architecture
- `features`: builds user-level feature table from raw CSVs
- `linkage`: scales features and computes Ward linkage matrix
- `cluster`: cuts dendrogram into clusters and writes outputs
- `report`: generates a human-readable report for a run
- `db` (optional): stores runs/features/clusters in SQLite

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt