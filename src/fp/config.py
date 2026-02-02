from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class ProjectConfig:
    # Provider IDs to exclude (your BBD list)
    excluded_provider_ids: List[int]

    # Minimum orders per user to keep
    min_orders_per_user: int

    # Default artifact locations
    artifacts_dir: Path


DEFAULT_CONFIG = ProjectConfig(
    excluded_provider_ids=[45191, 45276],
    min_orders_per_user=3,
    artifacts_dir=Path("artifacts"),
)
