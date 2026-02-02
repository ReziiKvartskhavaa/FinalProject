from __future__ import annotations

from pathlib import Path
import pandas as pd
from fp.io import read_csv


def generate_report(run_dir: str, out_path: str) -> None:
    run = Path(run_dir)
    meta_path = run / "run_meta.json"
    summary_path = run / "cluster_summary.csv"
    means_path = run / "cluster_means.csv"

    summary = read_csv(summary_path)
    means = read_csv(means_path)

    lines = []
    lines.append("# Clustering Report\n")

    # Meta (best-effort: if json not found, skip)
    if meta_path.exists():
        import json
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        lines.append("## Run Metadata")
        for k, v in meta.items():
            lines.append(f"- **{k}**: {v}")
        lines.append("")

    lines.append("## Cluster Summary")
    lines.append(summary.to_markdown(index=False))
    lines.append("")

    lines.append("## Cluster Profiles (means)")
    lines.append(means.to_markdown(index=False))
    lines.append("")

    # Auto “label hints” by top features per cluster
    if "Cluster" in means.columns:
        feature_cols = [c for c in means.columns if c != "Cluster"]
        lines.append("## Auto label hints")
        for _, row in means.iterrows():
            cl = int(row["Cluster"])
            top3 = sorted(feature_cols, key=lambda c: row[c], reverse=True)[:3]
            hint = ", ".join([f"{c}={row[c]:.2f}" for c in top3])
            lines.append(f"- Cluster **{cl}**: top features → {hint}")
        lines.append("")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
