# generate_seeds.py
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from data_gen_utils import (
    AmazonAdsSeedPipeline,
    GenerationConfig,
    DataRow,
    SeedTableSpec,
)


def default_identifier_overrides(use_integration_names: bool) -> Dict[str, str]:
    # If using the integration_tests seeds, map canonical table names to *_data filenames
    return {} if not use_integration_names else {
        "ad_group_history": "ad_group_history_data",
        "ad_group_level_report": "ad_group_level_report_data",
        "advertised_product_report": "advertised_product_report_data",
        "campaign_history": "campaign_history_data",
        "campaign_level_report": "campaign_level_report_data",
        "portfolio_history": "portfolio_history_data",
        "product_ad_history": "product_ad_history_data",
        "profile": "profile_data",
        "keyword_history": "keyword_history_data",
        "targeting_keyword_report": "targeting_keyword_report_data",
        "search_term_ad_keyword_report": "search_term_ad_keyword_report_data",
    }


def build_config(args: argparse.Namespace) -> GenerationConfig:
    if args.config is not None:
        return GenerationConfig.from_yaml(Path(args.config))

    # Default date horizon for reports: last 14 days
    from datetime import date, timedelta
    end = date.today()
    start = end - timedelta(days=14)

    return GenerationConfig(
        seed_dir=Path(args.seed_dir),
        output_dir=Path(args.out_dir),
        schema=args.schema,
        database=args.database,
        identifier_overrides=default_identifier_overrides(args.use_integration_identifiers),
        portfolio_enabled=not args.disable_portfolio,
        pass_through_metrics={},  # add if needed
        row_counts={
            # defaults; override via YAML or CLI later if you want
            "profile": 3,
            "campaign_history": 6,
            "ad_group_history": 10,
            "keyword_history": 20,
            "product_ad_history": 10,
            "portfolio_history": 2,
        },
        date_ranges={"default": (start.isoformat(), end.isoformat())},
        cpc_range=(0.3, 1.5),
        freshness_mode="recent",  # or "disabled"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Amazon Ads seeds and optionally run dbt.")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config (optional)")
    parser.add_argument("--catalog", type=str, default="docs/catalog_slim.json", help="Path to catalog json")
    parser.add_argument("--src-yml", type=str, default="models/src_amazon_ads.yml", help="Path to src yaml")
    parser.add_argument("--stg-yml", type=str, default="models/stg_amazon_ads.yml", help="Path to staging yaml")
    parser.add_argument("--seed-dir", type=str, default="integration_tests/seeds", help="Directory to read existing seeds from")
    parser.add_argument("--out-dir", type=str, default="seeds", help="Directory to write generated seeds to")
    parser.add_argument("--schema", type=str, default=None, help="Target schema (optional)")
    parser.add_argument("--database", type=str, default=None, help="Target database (optional)")
    parser.add_argument("--profiles-dir", type=str, default=None, help="dbt profiles dir (optional)")
    parser.add_argument("--project-dir", type=str, default=None, help="dbt project dir (optional)")
    parser.add_argument("--no-seed", action="store_true", help="Skip `dbt seed`")
    parser.add_argument("--no-build", action="store_true", help="Skip `dbt build`")
    parser.add_argument("--disable-portfolio", action="store_true", help="Disable portfolio_history generation")
    parser.add_argument("--use-integration-identifiers", action="store_true", help="Map identifiers to *_data seed names")
    args = parser.parse_args()

    # Build configuration
    cfg = build_config(args)

    pipeline = AmazonAdsSeedPipeline(cfg)
    pipeline.prepare_environment()

    # Discover specs (columns, required fields, unique keys)
    specs: Dict[str, SeedTableSpec] = pipeline.discover_specs(
        catalog_path=Path(args.catalog),
        src_yml_path=Path(args.src_yml),
        stg_yml_path=Path(args.stg_yml),
    )

    # Plan and generate
    order: List[str] = pipeline.plan_generation(specs)
    existing: Dict[str, List[DataRow]] = pipeline.read_existing_seeds()
    entity_rows: Dict[str, List[DataRow]] = pipeline.generate_entities(order, specs, existing)
    report_rows: Dict[str, List[DataRow]] = pipeline.generate_reports(specs, entity_rows)

    # Write and validate
    combined = {**entity_rows, **report_rows}
    pipeline.write_seeds(combined, specs)
    pipeline.validate_local(combined, specs)

    # Optional: run dbt
    run_seed = not args.no_seed
    run_build = not args.no_build
    if run_seed or run_build:
        pipeline.run_dbt(
            seed=run_seed,
            build=run_build,
            selector="amazon_ads_source",
            profiles_dir=Path(args.profiles_dir) if args.profiles_dir else None,
            project_dir=Path(args.project_dir) if args.project_dir else None,
        )

    print(pipeline.summary())


if __name__ == "__main__":
    main()
    
"""


- Run with defaults (uses integration seed names, writes to seeds/):

python generate_seeds.py --use-integration-identifiers

- Or with YAML:
python generate_seeds.py --config config.yml

- To execute dbt as well:
python generate_seeds.py --use-integration-identifiers --profiles-dir . --project-dir .

"""