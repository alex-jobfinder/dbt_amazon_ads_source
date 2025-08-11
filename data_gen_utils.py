"""

### Orchestrator
- `AmazonAdsSeedPipeline`
  - `prepare_environment(config: GenerationConfig)`: load config, set identifier/schema mappings.
  - `discover_specs()`: load schemas/types/order/tests from repo (catalog + yml + macros).
  - `plan_generation()`: build dependency graph and generation plan.
  - `generate_all()`: invoke entity/report generators in order.
  - `write_seeds()`: serialize rows to CSV with correct order/types.
  - `validate_local()`: run PK/FK/metric invariants.
  - `run_dbt(seed: bool = True, build: bool = True)`: run dbt seed/build to confirm tests.
  - `summary()`: emit run summary and next actions.

### Configuration and IO
- `GenerationConfig`
  - Fields: seed_dir, output_dir, row_counts, date_ranges, cpc_range, enums, portfolio_enabled, pass_through_metrics, identifier_overrides, schema/database targets, freshness_mode.
  - Methods: `from_yaml(path)`, `resolve_defaults(adapter)`.
- `SeedRepository`
  - `scan_existing()`: list existing seed CSVs and headers.
  - `read_csv(name)`: load rows and column order.
  - `write_csv(name, header, rows)`: write with stable ordering and quoting.
- `IdentifierMapper`
  - `seed_filename_for(table_identifier)`: map to `_data` names or defaults.
  - `apply_project_vars()`: compute vars for dbt identifier overrides.

### Spec extraction
- `CatalogReader`
  - `load(path)`: parse catalog_slim/catalog.
  - `seed_nodes()`: filter nodes starting with `seed.`.
  - `schema_for(seed_name)`: get ordered columns with types (by index).
- `SourceModelReader`
  - `load_src_models()`: parse `models/src_amazon_ads.yml`.
  - `required_columns(table)`: columns expected upstream (incl. `_fivetran_synced`).
  - `is_optional(table)`: e.g., `portfolio_history`.
- `StagingSpecReader`
  - `load_stg_specs()`: parse `models/stg_amazon_ads.yml`.
  - `uniqueness_keys(table)`: combinations for uniqueness.
  - `required_fields(table)`: not_null fields and semantic hints.
- `MacroColumnsReader`
  - `columns_for(table)`: read `macros/get_*_columns.sql` to list canonical staging columns.
  - `datatype_hints(table)`: adapter-agnostic types for fill/compat.

### Planning and relationships
- `DependencyPlanner`
  - `entity_order()`: profiles → campaigns → ad_groups → keywords/products.
  - `report_order()`: campaign/ad_group/advertised_product/targeting/search_term.
  - `fk_map()`: map child fields to parent pools (e.g., `campaign_history.profile_id → profile.id`).
- `EntityPools`
  - `register(table, key_field, ids)`: maintain PK pools.
  - `sample_fk(table, field)`: draw consistent FK values from parent pools.

### Value generation
- `TypeMapper`
  - `to_python(db_type)`: normalize adapter types to logical types.
  - `serialize(db_type, value)`: format for CSV (date/timestamp/decimal).
- `ColumnValueGenerator`
  - `generate(field, db_type, context)`: produce a plausible value.
  - Heuristics for names/states/status/match types; date/timestamp windows; decimals.
- `MetricsCalibrator`
  - `calibrate(row)`: enforce `impressions ≥ clicks ≥ 0`, `cost ≈ clicks*CPC`, `sales_30_d ≥ 0`, `purchases_30_d ≤ clicks`.
- `FreshnessManager`
  - `stamp_now(row)`: set `_fivetran_synced` recent or skip based on mode.

### Table generators
- `EntityGenerator`
  - `generate_profiles(n)`: PKs + attributes.
  - `generate_campaign_history(parent_profiles, per_parent)`.
  - `generate_ad_group_history(parent_campaigns, per_parent)`.
  - `generate_keyword_history(parent_ad_groups, per_parent)`.
  - `generate_product_ad_history(parent_ad_groups, per_parent)`.
- `ReportGenerator`
  - `generate_campaign_level_report(parent_campaigns, date_range)`.
  - `generate_ad_group_level_report(parent_ad_groups, date_range)`.
  - `generate_advertised_product_report(parent_ad_groups, date_range)`.
  - `generate_targeting_keyword_report(parent_keywords, date_range)`.
  - `generate_search_term_ad_keyword_report(parent_keywords, date_range)`.

### Validation and execution
- `LocalValidator`
  - `check_uniqueness(table, keys)`: dedupe/flag violations.
  - `check_foreign_keys(table, fk_map, pools)`: coverage checks.
  - `check_required_fields(table, required_fields)`.
  - `check_metrics(rows)`: invariant checks.
- `DbtExecutor`
  - `seed()`: run dbt seed with non-interactive flags.
  - `build(selector="amazon_ads_source")`: run dbt build/tests.
  - `status()`: collect failures and artifacts.

### Typical flow
- `prepare_environment` → `discover_specs` → `plan_generation` → `generate_all` → `write_seeds` → `validate_local` → `run_dbt` → `summary`.

- Summary
  - Defined an orchestrated pipeline with readers (catalog/src/stg/macros), planners (dependencies/FKs), generators (entities/reports), IO/typing (type map, writer), and validators (local + dbt) to produce realistic, test-passing seeds for all Amazon Ads source tables.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, TypedDict

import csv
import json
import random
import subprocess
from collections import defaultdict
from datetime import date, datetime, timedelta

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore


class DataRow(TypedDict, total=False):
    # Row keyed by column name; values are typed dynamically
    # Example: {"id": 123, "name": "Foo", "creation_date": "2024-01-01"}
    pass


@dataclass
class ColumnSpec:
    name: str
    db_type: str
    index: int
    comment: Optional[str] = None


@dataclass
class SeedTableSpec:
    table_name: str
    columns: List[ColumnSpec]
    unique_keys: List[str] = field(default_factory=list)
    required_fields: List[str] = field(default_factory=list)
    is_optional: bool = False


@dataclass
class GenerationConfig:
    seed_dir: Path
    output_dir: Path
    schema: Optional[str] = None
    database: Optional[str] = None
    identifier_overrides: Dict[str, str] = field(default_factory=dict)
    portfolio_enabled: bool = True
    pass_through_metrics: Dict[str, List[str]] = field(default_factory=dict)
    row_counts: Dict[str, int] = field(default_factory=dict)
    date_ranges: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    cpc_range: Tuple[float, float] = (0.3, 1.5)
    freshness_mode: str = "recent"  # "recent" | "disabled"

    @staticmethod
    def from_yaml(path: Path) -> "GenerationConfig":
        if yaml is None:
            raise RuntimeError("PyYAML is required to load GenerationConfig from YAML.")
        with path.open("r", encoding="utf-8") as f:
            raw: Dict[str, Any] = yaml.safe_load(f) or {}

        def to_path(maybe_path: Optional[str]) -> Optional[Path]:
            return Path(maybe_path) if isinstance(maybe_path, str) and maybe_path else None

        seed_dir = to_path(raw.get("seed_dir")) or Path("seeds")
        output_dir = to_path(raw.get("output_dir")) or seed_dir
        schema = raw.get("schema")
        database = raw.get("database")
        identifier_overrides = dict(raw.get("identifier_overrides") or {})
        portfolio_enabled = bool(raw.get("portfolio_enabled", True))
        pass_through_metrics = dict(raw.get("pass_through_metrics") or {})
        row_counts = dict(raw.get("row_counts") or {})
        date_ranges = dict(raw.get("date_ranges") or {})

        cpc_range_value = raw.get("cpc_range")
        if isinstance(cpc_range_value, (list, tuple)) and len(cpc_range_value) == 2:
            cpc_range = (float(cpc_range_value[0]), float(cpc_range_value[1]))
        else:
            cpc_range = (0.3, 1.5)

        freshness_mode = str(raw.get("freshness_mode", "recent"))

        return GenerationConfig(
            seed_dir=seed_dir,
            output_dir=output_dir,
            schema=schema,
            database=database,
            identifier_overrides=identifier_overrides,
            portfolio_enabled=portfolio_enabled,
            pass_through_metrics=pass_through_metrics,
            row_counts=row_counts,
            date_ranges=date_ranges,
            cpc_range=cpc_range,
            freshness_mode=freshness_mode,
        )


@dataclass
class DbtRunResult:
    seed_returncode: Optional[int]
    build_returncode: Optional[int]
    seed_stdout: Optional[str] = None
    seed_stderr: Optional[str] = None
    build_stdout: Optional[str] = None
    build_stderr: Optional[str] = None


class AmazonAdsSeedPipeline:
    # Class-level constants for convenience
    ENTITY_TABLES: Tuple[str, ...] = (
        "profile",
        "campaign_history",
        "ad_group_history",
        "keyword_history",
        "product_ad_history",
        "portfolio_history",  # gated by config.portfolio_enabled
    )
    REPORT_TABLES: Tuple[str, ...] = (
        "campaign_level_report",
        "ad_group_level_report",
        "advertised_product_report",
        "targeting_keyword_report",
        "search_term_ad_keyword_report",
    )

    def __init__(self, config: GenerationConfig) -> None:
        self.config: GenerationConfig = config
        self.specs: Dict[str, SeedTableSpec] = {}
        self.generation_order: List[str] = []
        self.entity_rows: Dict[str, List[DataRow]] = {}
        self.report_rows: Dict[str, List[DataRow]] = {}
        self.outputs: Dict[str, Path] = {}
        self.validation_errors: Dict[str, List[str]] = {}

    # Environment

    def prepare_environment(self) -> None:
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.seed_dir.mkdir(parents=True, exist_ok=True)

    # Spec discovery

    def discover_specs(
        self,
        catalog_path: Path,
        src_yml_path: Path,
        stg_yml_path: Path,
    ) -> Dict[str, SeedTableSpec]:
        specs: Dict[str, SeedTableSpec] = {}

        # Catalog-derived columns/order/types
        if catalog_path.exists():
            with catalog_path.open("r", encoding="utf-8") as f:
                catalog = json.load(f)
            nodes: Dict[str, Any] = catalog.get("nodes", {})
            for key, node in nodes.items():
                if not key.startswith("seed."):
                    continue
                md = node.get("metadata", {})
                seed_name: str = md.get("name") or key.split(".")[-1]
                cols = []
                for col_name, col in (node.get("columns", {}) or {}).items():
                    cols.append(ColumnSpec(
                        name=col.get("name", col_name),
                        db_type=str(col.get("type", "text")),
                        index=int(col.get("index", 10_000)),
                        comment=col.get("comment"),
                    ))
                cols.sort(key=lambda c: c.index)
                specs[seed_name] = SeedTableSpec(table_name=seed_name, columns=cols)

        # Required fields and optional flags from src models
        if yaml is not None and src_yml_path.exists():
            with src_yml_path.open("r", encoding="utf-8") as f:
                src_obj = yaml.safe_load(f) or {}
            for source in src_obj.get("sources", []) or []:
                for t in source.get("tables", []) or []:
                    canonical = t.get("name")
                    if not canonical:
                        continue
                    cols = [c.get("name") for c in (t.get("columns", []) or []) if c.get("name")]
                    target_name = self.apply_identifier_overrides(canonical)
                    spec = specs.get(target_name) or SeedTableSpec(table_name=target_name, columns=[])
                    spec.required_fields = list({*(spec.required_fields or []), *cols})
                    if canonical == "portfolio_history":
                        spec.is_optional = not self.config.portfolio_enabled
                    specs[target_name] = spec

        # Uniqueness keys from staging YAML
        if yaml is not None and stg_yml_path.exists():
            with stg_yml_path.open("r", encoding="utf-8") as f:
                stg_obj = yaml.safe_load(f) or {}
            for m in stg_obj.get("models", []) or []:
                mname = m.get("name", "")
                if not mname.startswith("stg_amazon_ads__"):
                    continue
                canonical = mname.replace("stg_amazon_ads__", "")
                unique_keys: List[str] = []
                for test in m.get("tests", []) or []:
                    if isinstance(test, dict) and "dbt_utils.unique_combination_of_columns" in test:
                        combo = test["dbt_utils.unique_combination_of_columns"].get("combination_of_columns")
                        if isinstance(combo, list):
                            unique_keys = [str(k) for k in combo]
                            break
                if unique_keys:
                    target_name = self.apply_identifier_overrides(canonical)
                    spec = specs.get(target_name) or SeedTableSpec(table_name=target_name, columns=[])
                    spec.unique_keys = unique_keys
                    specs[target_name] = spec

        self.specs = specs
        return specs

    # Planning

    def plan_generation(self, specs: Mapping[str, SeedTableSpec]) -> List[str]:
        order: List[str] = []
        for t in self.ENTITY_TABLES:
            seed_name = self.apply_identifier_overrides(t)
            if seed_name in specs and not specs[seed_name].is_optional:
                order.append(t)
        for t in self.REPORT_TABLES:
            seed_name = self.apply_identifier_overrides(t)
            if seed_name in specs:
                order.append(t)
        self.generation_order = order
        return order

    # Generation: entities

    def generate_entities(
        self,
        order: Sequence[str],
        specs: Mapping[str, SeedTableSpec],
        existing_seeds: Optional[Mapping[str, List[DataRow]]] = None,
    ) -> Dict[str, List[DataRow]]:
        rows_by_table: Dict[str, List[DataRow]] = {}

        profile_ids: List[str] = []
        campaigns: List[DataRow] = []
        ad_groups: List[DataRow] = []
        keywords: List[DataRow] = []
        product_ads: List[DataRow] = []

        now = datetime.utcnow()

        def rand_dt(from_days: int = 180) -> str:
            dt = now - timedelta(days=random.randint(0, from_days), seconds=random.randint(0, 86_400))
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")

        def ensure_synced(row: DataRow) -> None:
            if self.config.freshness_mode == "recent":
                row["_fivetran_synced"] = now.strftime("%Y-%m-%d %H:%M:%S.%f")

        for canonical in order:
            if canonical not in self.ENTITY_TABLES:
                continue
            seed_name = self.apply_identifier_overrides(canonical)
            spec = specs.get(seed_name)
            if spec is None:
                continue
            target_count = int(self.config.row_counts.get(canonical, 5))
            existing = list((existing_seeds or {}).get(seed_name, []))

            col_names = [c.name for c in (spec.columns or [])]
            table_rows: List[DataRow] = []

            if canonical == "profile":
                start_id = 1000
                for i in range(target_count):
                    pid = str(start_id + i)
                    row: DataRow = {
                        "id": pid,
                        "_fivetran_deleted": False,
                        "account_id": f"acct-{pid}",
                        "account_marketplace_string_id": "ATVPDKIKX0DER",
                        "account_name": f"Profile {pid}",
                        "account_sub_type": "seller",
                        "account_type": "seller",
                        "account_valid_payment_method": True,
                        "country_code": "US",
                        "currency_code": "USD",
                        "daily_budget": 0,
                        "timezone": "UTC",
                    }
                    row["creation_date"] = rand_dt(365)
                    row["last_updated_date"] = rand_dt(30)
                    ensure_synced(row)
                    row = {k: v for k, v in row.items() if not col_names or k in col_names}
                    table_rows.append(row)
                    profile_ids.append(pid)

            elif canonical == "campaign_history":
                start_id = 2000
                for i in range(target_count):
                    cid = str(start_id + i)
                    profile_id = random.choice(profile_ids) if profile_ids else str(1000)
                    row = {
                        "id": cid,
                        "profile_id": profile_id,
                        "name": f"Campaign {cid}",
                        "bidding_strategy": random.choice(["legacy", "auto", "manual"]),
                        "budget": round(random.uniform(10, 1000), 2),
                        "budget_type": random.choice(["daily", "lifetime"]),
                        "effective_budget": round(random.uniform(10, 1000), 2),
                        "start_date": (date.today() - timedelta(days=random.randint(10, 100))).isoformat(),
                        "end_date": None,
                        "serving_status": random.choice(["CAMPAIGN_STATUS_ENABLED", "CAMPAIGN_PAUSED"]),
                        "state": random.choice(["enabled", "paused", "archived"]),
                        "targeting_type": random.choice(["manual", "auto"]),
                    }
                    row["creation_date"] = rand_dt(365)
                    row["last_updated_date"] = rand_dt(30)
                    ensure_synced(row)
                    row = {k: v for k, v in row.items() if not col_names or k in col_names}
                    table_rows.append(row)
                    campaigns.append({"id": cid, "profile_id": profile_id})

            elif canonical == "ad_group_history":
                start_id = 3000
                for i in range(target_count):
                    aid = str(start_id + i)
                    camp = random.choice(campaigns) if campaigns else {"id": "2000"}
                    row = {
                        "id": aid,
                        "campaign_id": camp["id"],
                        "name": f"AdGroup {aid}",
                        "default_bid": round(random.uniform(0.2, 5.0), 2),
                        "serving_status": random.choice(["AD_GROUP_STATUS_ENABLED", "CAMPAIGN_PAUSED"]),
                        "state": random.choice(["enabled", "paused", "archived"]),
                    }
                    row["creation_date"] = rand_dt(365)
                    row["last_updated_date"] = rand_dt(30)
                    ensure_synced(row)
                    row = {k: v for k, v in row.items() if not col_names or k in col_names}
                    table_rows.append(row)
                    ad_groups.append({"id": aid, "campaign_id": camp["id"]})

            elif canonical == "keyword_history":
                start_id = 4000
                for i in range(target_count):
                    kid = str(start_id + i)
                    ag = random.choice(ad_groups) if ad_groups else {"id": "3000", "campaign_id": "2000"}
                    row = {
                        "id": kid,
                        "ad_group_id": ag["id"],
                        "campaign_id": ag["campaign_id"],
                        "keyword_text": f"kw_{kid}",
                        "match_type": random.choice(["BROAD", "PHRASE", "EXACT"]),
                        "native_language_keyword": f"kw_{kid}",
                        "native_language_locale": "en_US",
                        "serving_status": random.choice(["ENABLED", "PAUSED"]),
                        "state": random.choice(["enabled", "paused", "archived"]),
                        "bid": round(random.uniform(0.2, 3.0), 2),
                    }
                    row["creation_date"] = rand_dt(365)
                    row["last_updated_date"] = rand_dt(30)
                    ensure_synced(row)
                    row = {k: v for k, v in row.items() if not col_names or k in col_names}
                    table_rows.append(row)
                    keywords.append({"id": kid, "ad_group_id": ag["id"], "campaign_id": ag["campaign_id"]})

            elif canonical == "product_ad_history":
                start_id = 5000
                for i in range(target_count):
                    pid = str(start_id + i)
                    ag = random.choice(ad_groups) if ad_groups else {"id": "3000", "campaign_id": "2000"}
                    row = {
                        "id": pid,
                        "ad_group_id": ag["id"],
                        "campaign_id": ag["campaign_id"],
                        "asin": f"B0{random.randint(1000000, 9999999)}",
                        "sku": f"SKU-{pid}",
                        "serving_status": random.choice(["ENABLED", "PAUSED"]),
                        "state": random.choice(["enabled", "paused", "archived"]),
                    }
                    row["creation_date"] = rand_dt(365)
                    row["last_updated_date"] = rand_dt(30)
                    ensure_synced(row)
                    row = {k: v for k, v in row.items() if not col_names or k in col_names}
                    table_rows.append(row)
                    product_ads.append({"id": pid, "ad_group_id": ag["id"], "campaign_id": ag["campaign_id"]})

            elif canonical == "portfolio_history":
                if not self.config.portfolio_enabled:
                    continue
                start_id = 6000
                for i in range(target_count):
                    pfid = str(start_id + i)
                    row = {
                        "id": pfid,
                        "name": f"Portfolio {pfid}",
                        "budget_amount": round(random.uniform(100, 5000), 2),
                        "budget_currency_code": "USD",
                        "budget_policy": random.choice(["dateRange", "monthlyRecurring"]),
                        "in_budget": random.choice([True, False]),
                        "serving_status": random.choice(["ENABLED", "PAUSED"]),
                        "state": random.choice(["enabled", "paused", "archived"]),
                    }
                    row["creation_date"] = rand_dt(365)
                    row["last_updated_date"] = rand_dt(30)
                    row["budget_start_date"] = (date.today() - timedelta(days=random.randint(30, 180))).strftime("%Y%m%d")
                    row["budget_end_date"] = (date.today() + timedelta(days=random.randint(30, 180))).strftime("%Y%m%d")
                    ensure_synced(row)
                    row = {k: v for k, v in row.items() if not col_names or k in col_names}
                    table_rows.append(row)

            if existing:
                table_rows = list(existing) + table_rows
            rows_by_table[seed_name] = table_rows

        self.entity_rows = rows_by_table
        return rows_by_table

    # Generation: reports

    def generate_reports(
        self,
        specs: Mapping[str, SeedTableSpec],
        entity_rows: Mapping[str, List[DataRow]],
    ) -> Dict[str, List[DataRow]]:
        rows_by_table: Dict[str, List[DataRow]] = {}

        campaigns = {r.get("id"): r for r in entity_rows.get(self.apply_identifier_overrides("campaign_history"), [])}
        ad_groups = {r.get("id"): r for r in entity_rows.get(self.apply_identifier_overrides("ad_group_history"), [])}
        keywords = {r.get("id"): r for r in entity_rows.get(self.apply_identifier_overrides("keyword_history"), [])}
        product_ads = {r.get("id"): r for r in entity_rows.get(self.apply_identifier_overrides("product_ad_history"), [])}

        def parse_range(key: str, default_days: int) -> Tuple[date, date]:
            rng = self.config.date_ranges.get(key) or self.config.date_ranges.get("default")
            if rng and isinstance(rng, (list, tuple)) and len(rng) == 2:
                start = datetime.fromisoformat(str(rng[0])).date()
                end = datetime.fromisoformat(str(rng[1])).date()
            else:
                end = date.today()
                start = end - timedelta(days=default_days)
            return start, end

        def daterange(start_date: date, end_date: date):
            for n in range((end_date - start_date).days + 1):
                yield start_date + timedelta(n)

        def metric_row(base: DataRow) -> DataRow:
            clicks = max(0, int(random.gauss(3, 5)))
            impressions = max(clicks, clicks + int(abs(random.gauss(20, 50))))
            cpc = random.uniform(*self.config.cpc_range)
            cost = round(clicks * cpc, 2)
            purchases = max(0, min(clicks, int(random.gauss(1, 2))))
            sales = round(purchases * random.uniform(10, 100), 2)
            row: DataRow = dict(base)
            row.update({
                "clicks": clicks,
                "impressions": impressions,
                "cost": cost,
                "purchases_30_d": purchases,
                "sales_30_d": sales,
            })
            row["_fivetran_synced"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
            return row

        # campaign_level_report
        clr_name = self.apply_identifier_overrides("campaign_level_report")
        if clr_name in specs:
            start, end = parse_range("campaign_level_report", 14)
            col_names = [c.name for c in (specs[clr_name].columns or [])]
            rows: List[DataRow] = []
            for cid in campaigns.keys():
                for d in daterange(start, end):
                    base: DataRow = {"campaign_id": cid, "date": d.isoformat(), "campaign_bidding_strategy": random.choice(["legacy", "auto", "manual"]) }
                    row = metric_row(base)
                    rows.append({k: v for k, v in row.items() if not col_names or k in col_names})
            rows_by_table[clr_name] = rows

        # ad_group_level_report
        aglr_name = self.apply_identifier_overrides("ad_group_level_report")
        if aglr_name in specs:
            start, end = parse_range("ad_group_level_report", 14)
            col_names = [c.name for c in (specs[aglr_name].columns or [])]
            rows = []
            for agid in ad_groups.keys():
                for d in daterange(start, end):
                    base = {"ad_group_id": agid, "date": d.isoformat(), "campaign_bidding_strategy": random.choice(["legacy", "auto", "manual"]) }
                    row = metric_row(base)
                    rows.append({k: v for k, v in row.items() if not col_names or k in col_names})
            rows_by_table[aglr_name] = rows

        # advertised_product_report
        apr_name = self.apply_identifier_overrides("advertised_product_report")
        if apr_name in specs:
            start, end = parse_range("advertised_product_report", 14)
            col_names = [c.name for c in (specs[apr_name].columns or [])]
            rows = []
            for adid, ad in product_ads.items():
                agid = ad.get("ad_group_id")
                cid = ad.get("campaign_id")
                for d in daterange(start, end):
                    base = {
                        "ad_id": adid,
                        "ad_group_id": agid,
                        "campaign_id": cid,
                        "date": d.isoformat(),
                        "campaign_budget_amount": round(random.uniform(10, 1000), 2),
                        "campaign_budget_currency_code": "USD",
                        "campaign_budget_type": random.choice(["daily", "lifetime"]),
                    }
                    row = metric_row(base)
                    rows.append({k: v for k, v in row.items() if not col_names or k in col_names})
            rows_by_table[apr_name] = rows

        # targeting_keyword_report
        tkr_name = self.apply_identifier_overrides("targeting_keyword_report")
        if tkr_name in specs:
            start, end = parse_range("targeting_keyword_report", 14)
            col_names = [c.name for c in (specs[tkr_name].columns or [])]
            rows = []
            for kid, kw in keywords.items():
                agid = kw.get("ad_group_id")
                cid = kw.get("campaign_id")
                for d in daterange(start, end):
                    base = {
                        "keyword_id": kid,
                        "ad_group_id": agid,
                        "campaign_id": cid,
                        "date": d.isoformat(),
                        "ad_keyword_status": random.choice(["ENABLED", "PAUSED"]),
                        "keyword_bid": round(random.uniform(0.2, 3.0), 2),
                        "keyword_type": random.choice(["BROAD", "PHRASE", "EXACT"]),
                        "match_type": random.choice(["BROAD", "PHRASE", "EXACT"]),
                        "targeting": "TARGETING_EXPRESSION",
                        "campaign_budget_amount": round(random.uniform(10, 1000), 2),
                        "campaign_budget_currency_code": "USD",
                        "campaign_budget_type": random.choice(["daily", "lifetime"]),
                    }
                    row = metric_row(base)
                    rows.append({k: v for k, v in row.items() if not col_names or k in col_names})
            rows_by_table[tkr_name] = rows

        # search_term_ad_keyword_report
        star_name = self.apply_identifier_overrides("search_term_ad_keyword_report")
        if star_name in specs:
            start, end = parse_range("search_term_ad_keyword_report", 14)
            col_names = [c.name for c in (specs[star_name].columns or [])]
            rows = []
            for kid, kw in keywords.items():
                agid = kw.get("ad_group_id")
                cid = kw.get("campaign_id")
                for d in daterange(start, end):
                    base = {
                        "keyword_id": kid,
                        "ad_group_id": agid,
                        "campaign_id": cid,
                        "date": d.isoformat(),
                        "search_term": f"search for {kid}",
                        "ad_keyword_status": random.choice(["ENABLED", "PAUSED"]),
                        "keyword_bid": round(random.uniform(0.2, 3.0), 2),
                        "campaign_budget_amount": round(random.uniform(10, 1000), 2),
                        "campaign_budget_currency_code": "USD",
                        "campaign_budget_type": random.choice(["daily", "lifetime"]),
                        "targeting": "TARGETING_EXPRESSION",
                    }
                    row = metric_row(base)
                    rows.append({k: v for k, v in row.items() if not col_names or k in col_names})
            rows_by_table[star_name] = rows

        self.report_rows = rows_by_table
        return rows_by_table

    # IO

    def read_existing_seeds(self) -> Dict[str, List[DataRow]]:
        results: Dict[str, List[DataRow]] = {}
        if not self.config.seed_dir.exists():
            return results
        for path in self.config.seed_dir.glob("*.csv"):
            with path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows: List[DataRow] = []
                for r in reader:
                    rows.append({k: (v if v != "" else None) for k, v in r.items()})
                results[path.stem] = rows
        return results

    def write_seeds(
        self,
        rows_by_table: Mapping[str, List[DataRow]],
        specs: Mapping[str, SeedTableSpec],
    ) -> Dict[str, Path]:
        outputs: Dict[str, Path] = {}
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        for seed_name, rows in rows_by_table.items():
            spec = specs.get(seed_name)
            if spec and spec.columns:
                header = [c.name for c in spec.columns]
            else:
                inferred: List[str] = []
                for r in rows:
                    for k in r.keys():
                        if k not in inferred:
                            inferred.append(k)
                header = inferred
            out_path = self.config.output_dir / f"{seed_name}.csv"
            with out_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
                writer.writeheader()
                for r in rows:
                    writer.writerow({k: self.serialize_value(self._db_type_for(spec, k), r.get(k)) for k in header})
            outputs[seed_name] = out_path
        self.outputs = outputs
        return outputs

    def _db_type_for(self, spec: Optional[SeedTableSpec], col_name: str) -> str:
        if not spec:
            return "text"
        for c in spec.columns or []:
            if c.name == col_name:
                return c.db_type or "text"
        return "text"

    # Validation

    def validate_local(
        self,
        rows_by_table: Mapping[str, List[DataRow]],
        specs: Mapping[str, SeedTableSpec],
    ) -> Dict[str, List[str]]:
        errors: Dict[str, List[str]] = defaultdict(list)

        def check_unique(table: str, keys: List[str], rows: List[DataRow]) -> None:
            seen = set()
            for r in rows:
                tup = tuple(r.get(k) for k in keys)
                if tup in seen:
                    errors[table].append(f"duplicate unique combo {keys}: {tup}")
                else:
                    seen.add(tup)

        def check_required(table: str, req: List[str], rows: List[DataRow]) -> None:
            for idx, r in enumerate(rows):
                for k in req:
                    if k not in r or r.get(k) is None:
                        errors[table].append(f"row {idx} missing required field '{k}'")

        def check_metrics(table: str, rows: List[DataRow]) -> None:
            for idx, r in enumerate(rows):
                clicks = _to_int(r.get("clicks"))
                impressions = _to_int(r.get("impressions"))
                cost = _to_float(r.get("cost"))
                if impressions is not None and clicks is not None and impressions < clicks:
                    errors[table].append(f"row {idx} impressions < clicks")
                if clicks is not None and cost is not None and cost < 0:
                    errors[table].append(f"row {idx} negative cost")

        for seed_name, rows in rows_by_table.items():
            spec = specs.get(seed_name)
            if not spec:
                continue
            if spec.unique_keys:
                # Normalize staging keys to seed reality: drop source_relation, map date_day -> date
                norm_keys = [
                    ("date" if k == "date_day" else k)
                    for k in spec.unique_keys
                    if k != "source_relation"
                ]
                # Only enforce uniqueness if all keys exist in the seed rows
                header = set(rows[0].keys()) if rows else set()
                if norm_keys and all(k in header for k in norm_keys):
                    check_unique(seed_name, norm_keys, rows)
            if spec.required_fields:
                check_required(seed_name, spec.required_fields, rows)
            if any(seed_name.endswith(suf) for suf in ("_report", "_report_data")) or "report" in seed_name:
                check_metrics(seed_name, rows)

        self.validation_errors = dict(errors)
        return self.validation_errors

    # dbt execution

    def run_dbt(
        self,
        seed: bool = True,
        build: bool = True,
        selector: Optional[str] = "amazon_ads_source",
        profiles_dir: Optional[Path] = None,
        project_dir: Optional[Path] = None,
    ) -> DbtRunResult:
        def run_cmd(args: List[str]) -> Tuple[int, str, str]:
            try:
                proc = subprocess.run(args, capture_output=True, text=True, check=False)
                return proc.returncode, proc.stdout, proc.stderr
            except FileNotFoundError:
                return 127, "", "dbt not found"

        seed_rc: Optional[int] = None
        seed_out: Optional[str] = None
        seed_err: Optional[str] = None
        build_rc: Optional[int] = None
        build_out: Optional[str] = None
        build_err: Optional[str] = None

        if seed:
            cmd = ["dbt", "seed", "--full-refresh"]
            if profiles_dir:
                cmd += ["--profiles-dir", str(profiles_dir)]
            if project_dir:
                cmd += ["--project-dir", str(project_dir)]
            seed_rc, seed_out, seed_err = run_cmd(cmd)

        if build:
            cmd = ["dbt", "build"]
            if selector:
                cmd += ["-s", selector]
            if profiles_dir:
                cmd += ["--profiles-dir", str(profiles_dir)]
            if project_dir:
                cmd += ["--project-dir", str(project_dir)]
            build_rc, build_out, build_err = run_cmd(cmd)

        return DbtRunResult(
            seed_returncode=seed_rc,
            build_returncode=build_rc,
            seed_stdout=seed_out,
            seed_stderr=seed_err,
            build_stdout=build_out,
            build_stderr=build_err,
        )

    # Utilities

    def apply_identifier_overrides(self, table: str) -> str:
        return self.config.identifier_overrides.get(table, table)

    def serialize_value(self, db_type: str, value: Any) -> str:
        if value is None:
            return ""
        t = (db_type or "").lower()
        if "timestamp" in t:
            if isinstance(value, datetime):
                return value.strftime("%Y-%m-%d %H:%M:%S.%f")
            return str(value)
        if t == "date" or ("date" in t and "timestamp" not in t):
            if isinstance(value, (datetime, date)):
                return value.strftime("%Y-%m-%d")
            return str(value)
        if any(k in t for k in ("double", "float", "decimal", "numeric")):
            try:
                return f"{float(value):.2f}"
            except Exception:
                return str(value)
        return str(value)

    def summary(self) -> str:
        parts: List[str] = []
        parts.append(f"Generated entity tables: {sorted(self.entity_rows.keys())}")
        parts.append(f"Generated report tables: {sorted(self.report_rows.keys())}")
        if self.outputs:
            parts.append(f"Wrote {len(self.outputs)} seed files to {self.config.output_dir}")
        if self.validation_errors:
            total_errs = sum(len(v) for v in self.validation_errors.values())
            parts.append(f"Validation errors: {total_errs}")
        return "\n".join(parts)


# ---- helpers ----

def _to_int(v: Any) -> Optional[int]:
    try:
        if v is None or v == "":
            return None
        return int(v)
    except Exception:
        return None


def _to_float(v: Any) -> Optional[float]:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None