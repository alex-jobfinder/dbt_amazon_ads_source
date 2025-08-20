Alexa: Here’s the lean, end‑to‑end map of how campaigns are generated and tested (catalog‑driven).

### Generation (SQLite → CSV)
- • `scripts/sqlite_campaign_seed.py`: Catalog‑driven seed generator
  - Uses `--mode reset|append`, `--num-campaigns`, `--report-days`, `--catalog` (defaults to `docs/catalog_slim.json`).
  - Ensures or resets `campaigns` table with `id INTEGER PRIMARY KEY AUTOINCREMENT`.
  - Builds CSV headers from `docs/catalog_slim.json` column indexes/types and maps staging names to raw seed names where needed (e.g., `campaign_id → id`, `date_day → date`).
  - Writes `integration_tests/seeds/campaign_history_data.csv` and `integration_tests/seeds/campaign_level_report_data.csv` with coherent metrics.

- • `scripts/seed_core.py`: Shared helpers used by the generator
  - SQLite: connect, ensure/reset table.
  - Catalog: `load_catalog_columns` for (name, type, index).
  - CSV: typed writer; time/date helpers.

- • `integration_tests/dbt_project.yml`: Wire seeds to models
  - Map identifiers:
    - `amazon_ads_campaign_history_identifier: "campaign_history_data"`
    - `amazon_ads_campaign_level_report_identifier: "campaign_level_report_data"`
  - Optionally define pass-through metrics and seed column types.

- • `models_slim/src_amazon_ads.yml`: Declare sources and columns
  - Defines `campaign_history` and `campaign_level_report` sources, their identifiers, and expected columns used by dbt.

### Consumption (dbt tmp → staging)
- • `models_slim/tmp/stg_amazon_ads__campaign_history_tmp.sql`
  - Loads from `campaign_history_data` via `fivetran_utils.union_data` using schema/identifier vars.

- • `models_slim/stg_amazon_ads__campaign_history.sql`
  - Applies `fill_staging_columns`.
  - Renames/casts `id → campaign_id (string)`, `name → campaign_name`.
  - Computes `is_most_recent_record` by `row_number` over (`source_relation`, `id`) ordered by `last_updated_date`.

- • `models_slim/tmp/stg_amazon_ads__campaign_level_report_tmp.sql`
  - Loads from `campaign_level_report_data` via `union_data`.

- • `models_slim/stg_amazon_ads__campaign_level_report.sql`
  - Applies `fill_staging_columns`.
  - Casts `campaign_id` to string; `date → date_day`.
  - Adds optional pass-through metrics.

- • `models_slim/stg_amazon_ads.yml`
  - Tests uniqueness:
    - Campaign history: `[source_relation, campaign_id, last_updated_date]`.
    - Campaign level report: `[source_relation, campaign_id, date_day]`.
  - Documents column expectations.

### Testing (pytest)
- • `tests/test_sqlite_campaign_seed.py`: Validates generator behavior
  - reset mode: creates IDs `[1..N]`, writes both CSVs.
  - append mode: continues IDs sequentially across runs.
  - `campaign_history_data.csv`: header coverage; row count equals campaigns; IDs match DB.
  - `campaign_level_report_data.csv`: row count = campaigns × days; dates within window; metrics respect `impressions ≥ clicks ≥ 0` and `cost ≥ 0`.

- • `local/amazon_ads.sqlite`: Runtime DB file created for generation; used in tests within a temp directory.

Summary
- Generate with `sqlite_campaign_seed.py` (catalog‑driven) → writes `campaign_history_data.csv` and `campaign_level_report_data.csv`.
- dbt `src/tmp/stg` models read the CSVs via identifier vars, cast/rename, and enforce tests.
- Pytests confirm auto-increment IDs, CSV schema/row counts, date window, and metric invariants.







########

Alexa: Here are three practical ways to keep it simple and highly reusable.

- 1) Centralize a single, config-driven generator
  - Use one entrypoint/class (e.g., `SeedGenerator`) that reads schemas/types from `docs/catalog*.json` + `models_slim/src_amazon_ads.yml` and uniqueness from `models_slim/stg_amazon_ads.yml`.
  - Drive behavior via YAML (tables to emit, row counts, date ranges, identifier overrides, freshness mode) so new seed files require zero code.
  - Expose a consistent CLI: `--tables campaign_history,campaign_level_report --out-dir seeds --mode reset --report-days 14`.

- 2) Share core building blocks across all tables
  - Reuse a single I/O layer that writes CSVs with column order and types sourced from the catalog.
  - Keep FK integrity and metrics rules in shared utilities (e.g., `EntityPools`, `MetricsCalibrator`) so entities/reports reuse the same logic.
  - Provide small per-table generator functions registered in a table registry; default to generic type-based generation when no custom logic is needed.

- 3) Standardize testing and wiring
  - Create parametrized pytest fixtures to validate: headers match catalog, uniqueness keys hold, metrics invariants, date windows, and append/reset ID semantics.
  - Reuse the same generator in tests and local scripts to avoid drift; add a smoke test that runs `dbt seed` and `dbt build -s amazon_ads_source` on generated seeds.
  - Keep identifier mapping in one place (e.g., `GenerationConfig.yml`) and reflect it in both the generator and `dbt_project.yml` to eliminate duplicate configuration.

- Files to anchor
  - `data_gen_utils.py`: host shared components (schema readers, pools, metrics, writer).
  - `generate_seeds.py` and `scripts/sqlite_campaign_seed.py`: thin CLIs that delegate to the same generator.
  - `tests/`: parametrized tests that call the generator for any seed set.