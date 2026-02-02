from __future__ import annotations
import re
from typing import Dict, List
import pandas as pd


def clean_emojis(text: str) -> str:
    """
    Remove non-word symbols (including emoji) while keeping commas/spaces/words.
    """
    if not isinstance(text, str):
        return ""
    # Keep letters/numbers/underscore/space/comma
    return re.sub(r"[^\w\s,]", "", text)


def map_tags_to_clusters(tag_cell: str, mapping: Dict[str, str]) -> List[str]:
    """
    Split "tag1, tag2" -> [cluster1, cluster2] using mapping.
    Unknown tags become 'unknown'.
    """
    if not isinstance(tag_cell, str) or tag_cell.strip() == "":
        return []
    tag_list = [t.strip().lower() for t in tag_cell.split(",") if t.strip() != ""]
    out = []
    for t in tag_list:
        out.append(mapping.get(t, "unknown"))
    return out


def build_user_tag_cluster_percentages(
    tags_df: pd.DataFrame,
    orders_df: pd.DataFrame,
    tag_mapping: Dict[str, str],
    provider_id_col: str = "Provider ID",
    user_id_col: str = "User ID",
    provider_tag_col: str = "Provider Tag",
) -> pd.DataFrame:
    """
    Produces a wide df indexed by User ID with columns like 'asian','georgian',...
    values are percentage of tag-clusters across that user's orders/providers.
    """
    tags = tags_df.copy()
    tags = tags.dropna(subset=[provider_tag_col])
    tags[provider_tag_col] = tags[provider_tag_col].apply(clean_emojis)

    tags["Tag Clusters"] = tags[provider_tag_col].apply(lambda s: map_tags_to_clusters(s, tag_mapping))
    exploded = tags.explode("Tag Clusters")
    exploded = exploded[exploded["Tag Clusters"].notna()]

    merged = exploded.merge(
        orders_df[[provider_id_col, user_id_col]],
        on=provider_id_col,
        how="inner",
    )

    user_cluster_counts = merged.groupby([user_id_col, "Tag Clusters"]).size().reset_index(name="Count")
    totals = user_cluster_counts.groupby(user_id_col)["Count"].sum().reset_index(name="Total Count")
    pct = user_cluster_counts.merge(totals, on=user_id_col, how="left")
    pct["Percentage"] = (pct["Count"] / pct["Total Count"]) * 100.0

    wide = pct.pivot(index=user_id_col, columns="Tag Clusters", values="Percentage").fillna(0.0)

    # Ensure all clusters exist as columns
    for cluster in set(tag_mapping.values()):
        if cluster not in wide.columns:
            wide[cluster] = 0.0

    wide.reset_index(inplace=True)
    return wide
