# Variables (override via: make <target> VAR=value)
PYTHON ?= python3
PROJECT_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

CATALOG ?= $(PROJECT_ROOT)/docs/catalog.json
OUT_DIR ?= $(PROJECT_ROOT)/integration_tests/seeds
SQLITE_DB ?= $(PROJECT_ROOT)/local/amazon_ads.sqlite
DBT_PROFILES_DIR ?=

# Default dbt project directory for integration tests
DBT_PROJECT_DIR ?= $(PROJECT_ROOT)/integration_tests

# Comma-separated list of tables or 'all'
TABLES ?= profile,campaign_history,ad_group_history,keyword_history,product_ad_history,campaign_level_report
NUM_PER_PARENT ?= 3
REPORT_DAYS ?= 14

.PHONY: help sp-seed-reset sp-seed-append sqlite-campaign-reset sqlite-campaign-append dbt-seed dbt-build all load-sqlite

help:
	@echo "Targets:"
	@echo "  sp-seed-reset           - Generate seeds (unified generator) in reset mode"
	@echo "  sp-seed-append          - Generate seeds (unified generator) in append mode"
	@echo "  sqlite-campaign-reset   - Generate campaign seeds (SQLite) reset"
	@echo "  sqlite-campaign-append  - Generate campaign seeds (SQLite) append"
	@echo "  dbt-seed                - dbt seed --full-refresh"
	@echo "  dbt-build               - dbt build -s amazon_ads_source"
	@echo "Variables: TABLES=$(TABLES) NUM_PER_PARENT=$(NUM_PER_PARENT) REPORT_DAYS=$(REPORT_DAYS) CATALOG=$(CATALOG) OUT_DIR=$(OUT_DIR)"
	@echo "SQLITE_DB=$(SQLITE_DB)"

# Unified, catalog-driven generator (preferred)
sp-seed-reset:
	$(PYTHON) -m scripts.sp_seed \
		--tables $(TABLES) \
		--mode reset \
		--num-per-parent $(NUM_PER_PARENT) \
		--report-days $(REPORT_DAYS) \
		--catalog $(CATALOG) \
		--out-dir $(OUT_DIR)

sp-seed-append:
	$(PYTHON) -m scripts.sp_seed \
		--tables $(TABLES) \
		--mode append \
		--num-per-parent $(NUM_PER_PARENT) \
		--report-days $(REPORT_DAYS) \
		--catalog $(CATALOG) \
		--out-dir $(OUT_DIR)

# SQLite campaign-only generator (legacy/specific)
sqlite-campaign-reset:
	$(PYTHON) $(PROJECT_ROOT)/scripts/sqlite_campaign_seed.py --mode reset --out-dir $(OUT_DIR) --catalog $(CATALOG)

sqlite-campaign-append:
	$(PYTHON) $(PROJECT_ROOT)/scripts/sqlite_campaign_seed.py --mode append --out-dir $(OUT_DIR) --catalog $(CATALOG)

# dbt helpers
dbt-seed:
	dbt seed --full-refresh --project-dir $(DBT_PROJECT_DIR) $(if $(DBT_PROFILES_DIR),--profiles-dir $(DBT_PROFILES_DIR),)

dbt-build:
	dbt build -s amazon_ads_source --project-dir $(DBT_PROJECT_DIR) $(if $(DBT_PROFILES_DIR),--profiles-dir $(DBT_PROFILES_DIR),)



# Copy sample profiles if available
.PHONY: dbt-init-profiles
dbt-init-profiles:
	@mkdir -p $$HOME/.dbt
	@if [ -f "$(PROJECT_ROOT)/integration_tests/ci/sample.profiles.yml" ]; then \
		cp "$(PROJECT_ROOT)/integration_tests/ci/sample.profiles.yml" "$$HOME/.dbt/profiles.yml"; \
		echo "Installed sample profiles.yml to $$HOME/.dbt/profiles.yml"; \
	else \
		echo "No sample profiles found at integration_tests/ci/sample.profiles.yml"; \
	fi

# End-to-end (SQLite-only): generate (reset) then load into SQLite
all: sp-seed-reset load-sqlite

# Optional: End-to-end with dbt (kept for convenience)
.PHONY: all-dbt
all-dbt: sp-seed-reset dbt-seed dbt-build

# Load all generated CSVs into a SQLite database
load-sqlite:
	$(PYTHON) $(PROJECT_ROOT)/scripts/csv_to_sqlite.py --db $(SQLITE_DB) --in-dir $(OUT_DIR)


# python3 /home/alex/dbt_ads/0_dbt_source/dbt_amazon_ads_source/scripts/sqlite_campaign_seed.py --mode reset --num-campaigns 5 --report-days 14 --catalog /home/alex/dbt_ads/0_dbt_source/dbt_amazon_ads_source/docs/catalog_slim.json
# python3 /home/alex/dbt_ads/0_dbt_source/dbt_amazon_ads_source/scripts/sqlite_campaign_seed.py --mode append --num-campaigns 3 --report-days 14 --catalog /home/alex/dbt_ads/0_dbt_source/dbt_amazon_ads_source/docs/catalog_slim.json
# dbt seed --full-refresh
# dbt build -s amazon_ads_source


# make all
# # or explicitly:
# make sp-seed-reset load-sqlite



# sqlite3 /home/alex/dbt_ads/0_dbt_source/dbt_amazon_ads_source/local/amazon_ads.sqlite '.tables'