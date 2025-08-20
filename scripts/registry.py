from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import csv


@dataclass
class TableSpec:
    table_name: str                 # canonical table name (e.g., campaign_history)
    seed_name: str                  # seed csv base name (e.g., campaign_history_data)
    kind: str                       # "entity" | "report"
    grain: str                      # "history" | "daily"
    parents: List[Tuple[str, str, str]]  # [(parent_table, parent_pk, fk_field)]


def load_fk_map_from_csv(path: Path) -> Dict[str, List[Tuple[str, str, str]]]:
    """Parse models_slim/fk+pk.csv into {child_table: [(parent, parent_pk, fk_field), ...]}.

    Expected CSV columns include: child_table,parent_table,parent_pk,fk_field
    Extra columns are ignored.
    """
    fk_map: Dict[str, List[Tuple[str, str, str]]] = {}
    if not path.exists():
        return fk_map
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            child = (row.get("child_table") or "").strip()
            parent = (row.get("parent_table") or "").strip()
            parent_pk = (row.get("parent_pk") or "id").strip()
            fk_field = (row.get("fk_field") or "").strip()
            if not child or not parent or not fk_field:
                continue
            fk_map.setdefault(child, []).append((parent, parent_pk, fk_field))
    return fk_map


# Minimal built-in registry; extend as needed
REGISTRY: List[TableSpec] = [
    TableSpec("profile", "profile_data", "entity", "history", parents=[]),
    TableSpec(
        "campaign_history", "campaign_history_data", "entity", "history",
        parents=[("profile", "id", "profile_id")],
    ),
    TableSpec(
        "ad_group_history", "ad_group_history_data", "entity", "history",
        parents=[("campaign_history", "id", "campaign_id")],
    ),
    TableSpec(
        "product_ad_history", "product_ad_history_data", "entity", "history",
        parents=[("ad_group_history", "id", "ad_group_id")],
    ),
    TableSpec(
        "keyword_history", "keyword_history_data", "entity", "history",
        parents=[("ad_group_history", "id", "ad_group_id"), ("campaign_history", "id", "campaign_id")],
    ),
    TableSpec(
        "portfolio_history", "portfolio_history_data", "entity", "history",
        parents=[("campaign_history", "id", "campaign_id")],
    ),
    TableSpec(
        "campaign_level_report", "campaign_level_report_data", "report", "daily",
        parents=[("campaign_history", "id", "campaign_id")],
    ),
    TableSpec(
        "ad_group_level_report", "ad_group_level_report_data", "report", "daily",
        parents=[("ad_group_history", "id", "ad_group_id")],
    ),
    TableSpec(
        "advertised_product_report", "advertised_product_report_data", "report", "daily",
        parents=[("ad_group_history", "id", "ad_group_id")],
    ),
    TableSpec(
        "search_term_ad_keyword_report", "search_term_ad_keyword_report_data", "report", "daily",
        parents=[("ad_group_history", "id", "ad_group_id")],
    ),
    TableSpec(
        "targeting_keyword_report", "targeting_keyword_report_data", "report", "daily",
        parents=[("ad_group_history", "id", "ad_group_id")],
    ),
]


