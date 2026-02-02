from fp.cli import main

main()

# Run 1 — User Lifecycle & Engagement
# 1) Linkage
# PYTHONPATH=src python -m fp linkage \
#   --features artifacts/features.csv \
#   --feature-cols "Order Count" \
#   --feature-cols "Months Since Last Order" \
#   --feature-cols "AOV" \
#   --feature-cols "% of Targeted Campaigns" \
#   --feature-cols "paysWithCash" \
#   --feature-cols "Weekend" \
#   --feature-cols "Evening" \
#   --out artifacts/linkage_lifecycle.npy \
#   --meta artifacts/linkage_lifecycle_meta.json

# 2) Dendrogram (PNG)
# PYTHONPATH=src python -m fp dendrogram \
#   --features artifacts/features.csv \
#   --linkage artifacts/linkage_lifecycle.npy \
#   --feature-cols "Order Count" \
#   --feature-cols "Months Since Last Order" \
#   --feature-cols "AOV" \
#   --feature-cols "% of Targeted Campaigns" \
#   --feature-cols "paysWithCash" \
#   --feature-cols "Weekend" \
#   --feature-cols "Evening" \
#   --out artifacts/run_lifecycle_001/dendrogram.png \
#   --truncate-p 50

# 3) Cluster
# PYTHONPATH=src python -m fp cluster \
#   --features artifacts/features.csv \
#   --linkage artifacts/linkage_lifecycle.npy \
#   --feature-cols "Order Count" \
#   --feature-cols "Months Since Last Order" \
#   --feature-cols "AOV" \
#   --feature-cols "% of Targeted Campaigns" \
#   --feature-cols "paysWithCash" \
#   --feature-cols "Weekend" \
#   --feature-cols "Evening" \
#   --cut-distance 12 \
#   --out-dir artifacts/run_lifecycle_001

# 4) Report
# PYTHONPATH=src python -m fp report \
#   --run-dir artifacts/run_lifecycle_001 \
#   --out artifacts/run_lifecycle_001/report.md

# Run 2 — Service Quality & Reliability
# 1) Linkage
# PYTHONPATH=src python -m fp linkage \
#   --features artifacts/features.csv \
#   --feature-cols "ETA" \
#   --feature-cols "Average Order Full Time" \
#   --feature-cols "order_late" \
#   --feature-cols "fail_percentage" \
#   --feature-cols "Refund Percentage" \
#   --feature-cols "Provider Rating" \
#   --out artifacts/linkage_service.npy \
#   --meta artifacts/linkage_service_meta.json

# 2) Dendrogram (PNG)
# PYTHONPATH=src python -m fp dendrogram \
#   --features artifacts/features.csv \
#   --linkage artifacts/linkage_service.npy \
#   --feature-cols "ETA" \
#   --feature-cols "Average Order Full Time" \
#   --feature-cols "order_late" \
#   --feature-cols "fail_percentage" \
#   --feature-cols "Refund Percentage" \
#   --feature-cols "Provider Rating" \
#   --out artifacts/run_service_001/dendrogram.png \
#   --truncate-p 50

# 3) Cluster
# PYTHONPATH=src python -m fp cluster \
#   --features artifacts/features.csv \
#   --linkage artifacts/linkage_service.npy \
#   --feature-cols "ETA" \
#   --feature-cols "Average Order Full Time" \
#   --feature-cols "order_late" \
#   --feature-cols "fail_percentage" \
#   --feature-cols "Refund Percentage" \
#   --feature-cols "Provider Rating" \
#   --cut-distance 10 \
#   --out-dir artifacts/run_service_001

# 4) Report
# PYTHONPATH=src python -m fp report \
#   --run-dir artifacts/run_service_001 \
#   --out artifacts/run_service_001/report.md

# Run 3 — Commercial Sensitivity & Loyalty
# 1) Linkage
# PYTHONPATH=src python -m fp linkage \
#   --features artifacts/features.csv \
#   --feature-cols "Vendor Concentration" \
#   --feature-cols "GMV Discount Percentage" \
#   --feature-cols "% of Targeted Campaigns" \
#   --feature-cols "AOV" \
#   --feature-cols "Order Count" \
#   --feature-cols "paysWithCash" \
#   --out artifacts/linkage_commercial.npy \
#   --meta artifacts/linkage_commercial_meta.json

# 2) Dendrogram (PNG)
# PYTHONPATH=src python -m fp dendrogram \
#   --features artifacts/features.csv \
#   --linkage artifacts/linkage_commercial.npy \
#   --feature-cols "Vendor Concentration" \
#   --feature-cols "GMV Discount Percentage" \
#   --feature-cols "% of Targeted Campaigns" \
#   --feature-cols "AOV" \
#   --feature-cols "Order Count" \
#   --feature-cols "paysWithCash" \
#   --out artifacts/run_commercial_001/dendrogram.png \
#   --truncate-p 50

# 3) Cluster
# PYTHONPATH=src python -m fp cluster \
#   --features artifacts/features.csv \
#   --linkage artifacts/linkage_commercial.npy \
#   --feature-cols "Vendor Concentration" \
#   --feature-cols "GMV Discount Percentage" \
#   --feature-cols "% of Targeted Campaigns" \
#   --feature-cols "AOV" \
#   --feature-cols "Order Count" \
#   --feature-cols "paysWithCash" \
#   --cut-distance 10 \
#   --out-dir artifacts/run_commercial_001

# 4) Report
# PYTHONPATH=src python -m fp report \
#   --run-dir artifacts/run_commercial_001 \
#   --out artifacts/run_commercial_001/report.md