from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, List

try:
    # Module execution: python -m scripts.sp_seed
    from .seed_core import write_csv, load_catalog_columns, utc_ts
    from .registry import REGISTRY, TableSpec
    from .generators.entities import (
        generate_profiles,
        generate_campaign_history,
        generate_ad_group_history,
        generate_keyword_history,
        generate_product_ad_history,
        generate_portfolio_history,
    )
    from .generators.reports import (
        generate_campaign_level,
        generate_ad_group_level,
        generate_advertised_product,
        generate_search_term_ad_keyword,
        generate_targeting_keyword,
    )
except Exception:
    # Script execution: python scripts/sp_seed.py
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from seed_core import write_csv, load_catalog_columns, utc_ts  # type: ignore
    from registry import REGISTRY, TableSpec  # type: ignore
    from generators.entities import (  # type: ignore
        generate_profiles,
        generate_campaign_history,
        generate_ad_group_history,
        generate_keyword_history,
        generate_product_ad_history,
        generate_portfolio_history,
    )
    from generators.reports import (  # type: ignore
        generate_campaign_level,
        generate_ad_group_level,
        generate_advertised_product,
        generate_search_term_ad_keyword,
        generate_targeting_keyword,
    )


def build_header_from_catalog(catalog: Path, model_suffix: str, seed_mapping: Dict[str, str]) -> List[str]:
    cols = load_catalog_columns(catalog, model_suffix)
    header: List[str] = []
    for name, _t, _i in cols:
        mapped = seed_mapping.get(name, name)
        if mapped in ("source_relation", "is_most_recent_record"):
            continue
        if mapped not in header:
            header.append(mapped)
    if "_fivetran_synced" not in header:
        header.insert(2, "_fivetran_synced")
    return header


def main() -> None:
    parser = argparse.ArgumentParser(description="SP seed generator (catalog-driven)")
    parser.add_argument("--tables", type=str, default="all", help="Comma list or 'all'")
    parser.add_argument("--mode", type=str, choices=["reset", "append"], default="append")
    parser.add_argument("--num-per-parent", type=int, default=5)
    parser.add_argument("--report-days", type=int, default=14)
    parser.add_argument("--catalog", type=str, default=str(Path(__file__).resolve().parents[1] / "docs" / "catalog.json"))
    parser.add_argument("--out-dir", type=str, default="integration_tests/seeds")
    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sel = [t.strip() for t in args.tables.split(",")] if args.tables != "all" else []
    selected_specs = [s for s in REGISTRY if not sel or s.table_name in sel]

    # Pools for FKs
    profiles: List[str] = []
    campaigns: List[str] = []
    ad_groups: List[str] = []


    for spec in selected_specs:
        if spec.kind == "entity":
            if spec.table_name == "profile":
                rows = generate_profiles(args.num_per_parent)
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__profile", {})
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows)
                profiles = [r["id"] for r in rows]

            elif spec.table_name == "campaign_history":
                rows = generate_campaign_history(profiles, args.num_per_parent)
                mapping = {"campaign_id": "id", "campaign_name": "name"}
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__campaign_history", mapping)
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows)
                campaigns = [r["id"] for r in rows]

            elif spec.table_name == "ad_group_history":
                rows = generate_ad_group_history(campaigns, args.num_per_parent)
                mapping = {"ad_group_id": "id", "ad_group_name": "name"}
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__ad_group_history", mapping)
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows)
                ad_groups = [r["id"] for r in rows]

            elif spec.table_name == "keyword_history":
                rows = generate_keyword_history(ad_groups, campaigns, args.num_per_parent)
                mapping = {"keyword_id": "id"}
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__keyword_history", mapping)
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows)

            elif spec.table_name == "product_ad_history":
                rows = generate_product_ad_history(ad_groups, campaigns, args.num_per_parent)
                mapping = {"product_ad_id": "id"}
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__product_ad_history", mapping)
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows)

            elif spec.table_name == "portfolio_history":
                rows = generate_portfolio_history(campaigns, args.num_per_parent)
                mapping = {"portfolio_id": "id"}
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__portfolio_history", mapping)
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows)

        elif spec.kind == "report":
            if spec.table_name == "campaign_level_report":
                mapping = {"date_day": "date"}
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__campaign_level_report", mapping)
                rows_iter = generate_campaign_level(campaigns, args.report_days)
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows_iter)
            
            elif spec.table_name == "ad_group_level_report":
                mapping = {"date_day": "date"}
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__ad_group_level_report", mapping)
                rows_iter = generate_ad_group_level(ad_groups, args.report_days)
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows_iter)

            elif spec.table_name == "advertised_product_report":
                mapping = {"date_day": "date"}
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__advertised_product_report", mapping)
                rows_iter = generate_advertised_product(ad_groups, args.report_days)
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows_iter)
            
            elif spec.table_name == "search_term_ad_keyword_report":
                mapping = {"date_day": "date"}
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__search_term_ad_keyword_report", mapping)
                rows_iter = generate_search_term_ad_keyword(ad_groups, args.report_days)
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows_iter)
            
            elif spec.table_name == "targeting_keyword_report":
                mapping = {"date_day": "date"}
                header = build_header_from_catalog(catalog_path, "stg_amazon_ads__targeting_keyword_report", mapping)
                rows_iter = generate_targeting_keyword(ad_groups, args.report_days)
                write_csv(out_dir / f"{spec.seed_name}.csv", header, rows_iter)

    print(f"Wrote seeds to {out_dir}")


if __name__ == "__main__":
    main()


# "profile": "stg_amazon_ads__profile",

# "ad_group_history": "stg_amazon_ads__ad_group_history",
# "campaign_history": "stg_amazon_ads__campaign_history",
# "keyword_history": "stg_amazon_ads__keyword_history",
# "portfolio_history": "stg_amazon_ads__portfolio_history",
# "product_ad_history": "stg_amazon_ads__product_ad_history",

# "ad_group_level_report": "stg_amazon_ads__ad_group_level_report",
# "advertised_product_report": "stg_amazon_ads__advertised_product_report",
# "campaign_level_report": "stg_amazon_ads__campaign_level_report",
# "search_term_ad_keyword_report": "stg_amazon_ads__search_term_ad_keyword_report",
# "targeting_keyword_report": "stg_amazon_ads__targeting_keyword_report",