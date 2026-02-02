from __future__ import annotations

import typer
from typing import List, Optional

from fp.features import build_features
from fp.linkage import compute_linkage
from fp.cluster import cut_clusters
from fp.report import generate_report
from fp.dendrogram import plot_dendrogram

app = typer.Typer(help="Final Project CLI: features -> linkage -> cluster -> report")

@app.command()
def dendrogram(
    features: str = typer.Option(..., help="Features CSV"),
    linkage: str = typer.Option(..., help="Linkage .npy"),
    feature_cols: List[str] = typer.Option(..., help="Columns used for clustering"),
    out: str = typer.Option("artifacts/dendrogram.png", help="Output PNG"),
    truncate_p: int = typer.Option(50, help="How many clusters to show"),
    max_rows: int = typer.Option(40000, help="Max rows"),
):
    plot_dendrogram(
        features_csv=features,
        linkage_npy=linkage,
        feature_cols=feature_cols,
        out_png=out,
        truncate_p=truncate_p,
        max_rows=max_rows,
    )

@app.command()
def features(
    orders: str = typer.Option(..., help="Orders CSV path or filename"),
    zones: str = typer.Option(..., help="Zones CSV path or filename"),
    tags: str = typer.Option(..., help="Provider tags CSV path or filename"),
    data_dir: str = typer.Option(
        "/Users/revazkvartskhava/PycharmProjects/Mrkt",
        help="Directory where the CSVs live (used when you pass only filenames)",
    ),
    out: str = typer.Option("artifacts/features.csv", help="Output features CSV"),
    min_orders: int = typer.Option(3, help="Minimum orders per user"),
):
    build_features(
        orders_path=orders,
        zones_path=zones,
        tags_path=tags,
        out_path=out,
        data_dir=data_dir,
        min_orders_per_user=min_orders,
    )
    typer.echo(f"✅ Wrote features to {out}")


@app.command()
def linkage(
    features: str = typer.Option(..., help="Features CSV"),
    feature_cols: List[str] = typer.Option(..., help="Columns to use for clustering"),
    out: str = typer.Option("artifacts/linkage.npy", help="Output linkage .npy"),
    meta: str = typer.Option("artifacts/linkage_meta.json", help="Output metadata JSON"),
    method: str = typer.Option("ward", help="Linkage method"),
    no_scale: bool = typer.Option(False, help="Disable scaling"),
    max_rows: int = typer.Option(40000, help="Max rows to use"),
):
    compute_linkage(
        features_csv=features,
        feature_cols=feature_cols,
        out_npy=out,
        meta_json=meta,
        method=method,
        scale=not no_scale,
        max_rows=max_rows,
    )
    typer.echo(f"✅ Wrote linkage to {out} and meta to {meta}")


@app.command()
def cluster(
    features: str = typer.Option(..., help="Features CSV"),
    linkage: str = typer.Option(..., help="Linkage .npy"),
    feature_cols: List[str] = typer.Option(..., help="Columns to use for clustering"),
    out_dir: str = typer.Option(..., help="Output run directory"),
    cut_distance: Optional[float] = typer.Option(None, help="Cut distance (distance criterion)"),
    n_clusters: Optional[int] = typer.Option(None, help="Number of clusters (maxclust criterion)"),
    max_rows: int = typer.Option(40000, help="Max rows to use"),
):
    cut_clusters(
        features_csv=features,
        linkage_npy=linkage,
        feature_cols=feature_cols,
        out_dir=out_dir,
        cut_distance=cut_distance,
        n_clusters=n_clusters,
        max_rows=max_rows,
    )
    typer.echo(f"✅ Wrote clustering outputs to {out_dir}")


@app.command()
def report(
    run_dir: str = typer.Option(..., help="Run output directory (contains cluster_summary.csv etc.)"),
    out: str = typer.Option(..., help="Output report path (.md)"),
):
    generate_report(run_dir=run_dir, out_path=out)
    typer.echo(f"✅ Wrote report to {out}")


def main():
    app()


if __name__ == "__main__":
    main()
