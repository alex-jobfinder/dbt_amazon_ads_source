# Amazon Ads Source dbt Package ([Docs](https://fivetran.github.io/dbt_amazon_ads_source/))

<p align="left">
    <a alt="License"
        href="https://github.com/fivetran/dbt_amazon_ads_source/blob/main/LICENSE">
        <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" /></a>
    <a alt="dbt-core">
        <img src="https://img.shields.io/badge/dbt_Core™_version->=1.3.0_<2.0.0-orange.svg" /></a>
    <a alt="Maintained?">
        <img src="https://img.shields.io/badge/Maintained%3F-yes-green.svg" /></a>
    <a alt="PRs">
        <img src="https://img.shields.io/badge/Contributions-welcome-blueviolet" /></a>
</p>

## What does this dbt package do?
- Materializes [Amazon Ads staging tables](https://fivetran.github.io/dbt_amazon_ads_source/#!/overview/amazon_ads_source/models/?g_v=1&g_e=seeds), which leverage data in the format described by [this ERD](https://fivetran.com/docs/applications/amazon-ads#schemainformation). These staging tables clean, test, and prepare your Amazon Ads data from [Fivetran's connector](https://fivetran.com/docs/applications/amazon-ads) for analysis by doing the following:
  - Names columns for consistency across all packages and for easier analysis
  - Adds freshness tests to source data
    > dbt Core >= 1.9.6 is required to run freshness tests out of the box. See other options [here](https://github.com/fivetran/dbt_amazon_ads_source/blob/main/CHANGELOG.md#breaking-change-for-dbt-core--196).
  - Adds column-level testing where applicable. For example, all primary keys are tested for uniqueness and non-null values.
- Generates a comprehensive data dictionary of your Amazon Ads data through the [dbt docs site](https://fivetran.github.io/dbt_amazon_ads_source/).
- These tables are designed to work simultaneously with our [Amazon Ads transformation package](https://github.com/fivetran/dbt_amazon_ads).

## How do I use the dbt package?
### Step 1: Prerequisites
To use this dbt package, you must have the following:

- At least one Fivetran Amazon_ads connection syncing data into your destination.
- A **BigQuery**, **Snowflake**, **Redshift**, **PostgreSQL**, or **Databricks** destination.

### Step 2: Install the package (skip if also using the `amazon_ads` transformation package or `ad_reporting` combo package)
If you  are **not** using the [Amazon Ads transformation package](https://github.com/fivetran/dbt_amazon_ads) or the [Ad Reporting combination package](https://github.com/fivetran/dbt_ad_reporting), include the following `amazon_ads_source` package version in your `packages.yml` file.
> TIP: Check [dbt Hub](https://hub.getdbt.com/) for the latest installation instructions, or [read dbt's Package Management documentation](https://docs.getdbt.com/docs/package-management) for more information on installing packages.
```yaml
packages:
  - package: fivetran/amazon_ads_source
    version: [">=0.5.0", "<0.6.0"] # we recommend using ranges to capture non-breaking changes automatically
```

### Step 3: Define database and schema variables
By default, this package runs using your destination and the `amazon_ads` schema. If this is not where your Amazon_ads data is (for example, if your Amazon_ads schema is named `amazon_ads_fivetran`), add the following configuration to your root `dbt_project.yml` file:

```yml
vars:
  amazon_ads_database: your_database_name
  amazon_ads_schema: your_schema_name 
```

### Step 4: Disable models for non-existent sources
Your Amazon Ads connection may not sync every table that this package expects. If you do not have the `PORTFOLIO_HISTORY` table synced, add the following variable to your root `dbt_project.yml` file:

```yml
vars:
    amazon_ads__portfolio_history_enabled: False   # Disable if you do not have the portfolio table. Default is True.
```

### (Optional) Step 5: Additional configurations
<details open><summary>Expand/Collapse details</summary>

#### Union multiple connections
If you have multiple amazon_ads connections in Fivetran and would like to use this package on all of them simultaneously, we have provided functionality to do so. The package will union all of the data together and pass the unioned table into the transformations. You will be able to see which source it came from in the `source_relation` column of each model. To use this functionality, you will need to set either the `amazon_ads_union_schemas` OR `amazon_ads_union_databases` variables (cannot do both) in your root `dbt_project.yml` file:

```yml
vars:
    amazon_ads_union_schemas: ['amazon_ads_usa','amazon_ads_canada'] # use this if the data is in different schemas/datasets of the same database/project
    amazon_ads_union_databases: ['amazon_ads_usa','amazon_ads_canada'] # use this if the data is in different databases/projects but uses the same schema name
```
> NOTE: The native `source.yml` connection set up in the package will not function when the union schema/database feature is utilized. Although the data will be correctly combined, you will not observe the sources linked to the package models in the Directed Acyclic Graph (DAG). This happens because the package includes only one defined `source.yml`.

To connect your multiple schema/database sources to the package models, follow the steps outlined in the [Union Data Defined Sources Configuration](https://github.com/fivetran/dbt_fivetran_utils/tree/releases/v0.4.latest#union_data-source) section of the Fivetran Utils documentation for the union_data macro. This will ensure a proper configuration and correct visualization of connections in the DAG.

#### Passing Through Additional Metrics
By default, this package will select `clicks`, `impressions`, `cost`, `purchases_30_d`, and `sales_30_d` from the source reporting tables to store into the staging models. If you would like to pass through additional metrics to the staging models, add the following configurations to your `dbt_project.yml` file. These variables allow the pass-through fields to be aliased (`alias`) and transformed (`transform_sql`) if desired, but not required. Use the following format for declaring the respective pass-through variables:

> **Note** Ensure you exercised due diligence when adding metrics to these models. The metrics added by default (clicks, impressions, cost, purchases, and sales amount) have been vetted by the Fivetran team maintaining this package for accuracy. There are metrics included within the source reports, for example, metric averages, which may be inaccurately represented at the grain for reports created in this package. You want to ensure whichever metrics you pass through are indeed appropriate to aggregate at the respective reporting levels provided in this package.

```yml
vars:
    amazon_ads__campaign_passthrough_metrics: 
      - name: "new_custom_field"
        alias: "custom_field"
    amazon_ads__ad_group_passthrough_metrics:
      - name: "unique_string_field"
        transform_sql: "coalesce(unique_string_field, 'NA')"
    amazon_ads__advertised_product_passthrough_metrics: 
      - name: "new_custom_field"
        alias: "custom_field"
        transform_sql: "coalesce(custom_field, 'NA')" # reference alias in transform_sql if aliasing 
      - name: "a_second_field"
    amazon_ads__targeting_keyword_passthrough_metrics:
      - name: "this_field"
    amazon_ads__search_term_ad_keyword_passthrough_metrics:
      - name: "unique_string_field"
        alias: "field_id"
```

#### Changing the Build Schema
By default, this package will build the Amazon_ads staging models (11 views, 11 tables) within a schema titled (<target_schema> + `amazon_ads_source`) in your destination. If this is not where you would like your Amazon Ads staging data to be written, add the following configuration to your root `dbt_project.yml` file:

```yml
models:
    amazon_ads_source:
      +schema: my_new_schema_name # leave blank for just the target_schema
```

#### Change the source table references
If an individual source table has a different name than the package expects, add the table name as it appears in your destination to the respective variable. (This is not available when running the package on multiple unioned connections):

> IMPORTANT: See this project's [`dbt_project.yml`](https://github.com/fivetran/dbt_amazon_ads_source/blob/main/dbt_project.yml) variable declarations to see the expected names.

```yml
vars:
    amazon_ads_<default_source_table_name>_identifier: your_table_name 
```

</details>

### (Optional) Step 6: Orchestrate your models with Fivetran Transformations for dbt Core™
<details><summary>Expand for more details</summary>

Fivetran offers the ability for you to orchestrate your dbt project through [Fivetran Transformations for dbt Core™](https://fivetran.com/docs/transformations/dbt). Learn how to set up your project for orchestration through Fivetran in our [Transformations for dbt Core™ setup guides](https://fivetran.com/docs/transformations/dbt#setupguide).
    
</details>

## Does this package have dependencies?
This dbt package is dependent on the following dbt packages. Be aware that these dependencies are installed by default within this package. For more information on the following packages, refer to the [dbt hub](https://hub.getdbt.com/) site.
> IMPORTANT: If you have any of these dependent packages in your own `packages.yml` file, we highly recommend that you remove them from your root `packages.yml` to avoid package version conflicts.
```yml
packages:
    - package: fivetran/fivetran_utils
      version: [">=0.4.0", "<0.5.0"]

    - package: dbt-labs/dbt_utils
      version: [">=1.0.0", "<2.0.0"]
```
## How is this package maintained and can I contribute?
### Package Maintenance
The Fivetran team maintaining this package _only_ maintains the latest version of the package. We highly recommend that you stay consistent with the [latest version](https://hub.getdbt.com/fivetran/amazon_ads_source/latest/) of the package and refer to the [CHANGELOG](https://github.com/fivetran/dbt_amazon_ads_source/blob/main/CHANGELOG.md) and release notes for more information on changes across versions.

### Contributions
A small team of analytics engineers at Fivetran develops these dbt packages. However, the packages are made better by community contributions.

We highly encourage and welcome contributions to this package. Check out [this dbt Discourse article](https://discourse.getdbt.com/t/contributing-to-a-dbt-package/657) on the best workflow for contributing to a package.

#### Contributors
We thank [everyone](https://github.com/fivetran/amazon_ads_source/graphs/contributors) who has taken the time to contribute. Each PR, bug report, and feature request has made this package better and is truly appreciated.

A special thank you to [Seer Interactive](https://www.seerinteractive.com/?utm_campaign=Fivetran%20%7C%20Models&utm_source=Fivetran&utm_medium=Fivetran%20Documentation), who we closely collaborated with to introduce native conversion support to our Ad packages.

## Are there any resources available?
- If you have questions or want to reach out for help, see the [GitHub Issue](https://github.com/fivetran/dbt_amazon_ads_source/issues/new/choose) section to find the right avenue of support for you.
- If you would like to provide feedback to the dbt package team at Fivetran or would like to request a new dbt package, fill out our [Feedback Form](https://www.surveymonkey.com/r/DQ7K7WW).



## Goal:

**Goal:** Run `dbt_amazon_ads_source` without real Amazon Ads data from the Fivetran connector by:

* Using **dbt seeds** with example data
* Leveraging **package-defined tables, column types, and dbt logic**
* Generating **fake, schema-accurate data** for the staging tables
* Enabling **all transformations, tests, and docs** to function as if real data existed

**Summary:** *Simulate Amazon Ads source data for `dbt_amazon_ads_source` using seeds and schema-based fake data generation so the package can be run and tested without the Fivetran connector.*

**Step 1:** Create a document that reviews each relevant subdirectory and file in the package, describing:

* How the file’s data or logic could be used to support fake data generation
* Which files define schemas, tests, or transformation logic that can guide seed creation
* Any dependencies or references that must be considered when generating or linking the fake data

Alexa: Below is a concise guide to the key parts of this package you can leverage to generate fake, schema-accurate seed data that passes the package’s models and tests.

### Models

- `models/src_amazon_ads.yml`
  - How it helps: Canonical list of upstream source tables, expected column names, and the `_fivetran_synced` freshness field.
  - Guides: Source names vs identifiers (e.g., `amazon_ads_ad_group_history_identifier`), required columns, and optional `portfolio_history` via `amazon_ads__portfolio_history_enabled`.
  - Dependencies: Freshness checks on `_fivetran_synced`; model enabling via `ad_reporting__amazon_ads_enabled`.

- `models/tmp/*.sql` (e.g., `stg_amazon_ads__ad_group_history_tmp.sql`)
  - How it helps: Shows how each staging model reads its source using `fivetran_utils.union_data`.
  - Guides: Which table identifiers the package expects (e.g., `ad_group_history`) and which vars control schema/database (`amazon_ads_schema`, `amazon_ads_database`).
  - Dependencies: If you keep defaults, name seed files to match identifiers or set the identifier vars to your seed filenames.

- `models/stg_*.sql` (e.g., `stg_amazon_ads__ad_group_history.sql`)
  - How it helps: Shows casts/renames and the exact fields downstream expect (e.g., `id` becomes `ad_group_id`).
  - Guides: Which columns must be present in seeds and how they’re interpreted; supports selecting plausible value ranges.
  - Dependencies: Uses macros like `fill_staging_columns` and the per-table `get_*_columns` macro outputs.

- `models/stg_amazon_ads.yml`
  - How it helps: Centralized tests and final column expectations for each staging model.
  - Guides: Unique keys and grain for generating coherent data:
    - Example: `stg_amazon_ads__ad_group_history` unique on `[source_relation, ad_group_id, last_updated_date]`.
    - Reporting tables are unique on combinations like `[source_relation, ad_group_id, date_day]`.
  - Dependencies: Use this file to ensure PK uniqueness, FK coverage, daily report grains, and required fields.

- `models/docs.md`
  - How it helps: Field-level semantics (e.g., what “state”, “serving_status”, “match_type” mean).
  - Guides: Generate realistic categorical values and consistent metric relationships (clicks, impressions, cost, purchases, sales).
  - Dependencies: Align enums/values to these definitions to avoid downstream test surprises.

### Macros

- `macros/get_*_columns.sql` (e.g., `get_ad_group_history_columns.sql`)
  - How it helps: Defines the canonical set of staging columns and expected datatypes for `fill_staging_columns`.
  - Guides: Ensure your seeds provide at least these columns; use as the ground truth for minimal viable columns.
  - Dependencies: These columns drive the staging outputs; missing columns lead to nulls or failures depending on model logic/tests.

- `macros/amazon_ads_add_pass_though_columns.sql` and `macros/amazon_ads_fill_pass_through_columns.sql`
  - How it helps: Implements pass-through metric handling if you set the `amazon_ads__*_passthrough_metrics` vars.
  - Guides: If you intend to test pass-through metrics, include those extra columns in the corresponding report seeds.
  - Dependencies: Optional; driven by vars, but seeds must include the extra fields for them to propagate.

### Docs artifacts

- `docs/catalog.json` and `docs/catalog_slim.json`
  - How it helps: Adapter-native column types and canonical column ordering via `index`.
  - Guides: Map db types to generators (int/float/date/timestamp/text) and write CSV headers in the order of `index`.
  - Dependencies: Ensures seeds load with correct coercion/typing across adapters; improves test/build reliability.

- `docs/manifest.json`
  - How it helps: Full DAG, nodes, refs, and macro lineage.
  - Guides: Useful to debug dependencies or verify that sources map correctly after seeding.
  - Dependencies: Optional for generation; helpful for troubleshooting ref/source resolution.

### Integration tests

- `integration_tests/seeds/*.csv`
  - How it helps: Minimal, working CSV examples for every upstream table (e.g., `ad_group_history_data.csv`).
  - Guides: Valid headers, sample categorical values, and basic data shapes. Copy or “top up” volume as needed.
  - Dependencies: If you keep the `_data` suffix, set identifier vars (see below). Good baseline for enums like `state` and `serving_status`.

- `integration_tests/dbt_project.yml`
  - How it helps: Shows how to point package identifiers at the integration seed filenames and how to set seed column types.
  - Guides: Patterns to configure:
    - Identifier remaps (e.g., `amazon_ads_ad_group_history_identifier: "ad_group_history_data"`).
    - Seeds `+column_types` and `+quote_columns` for stricter adapters.
    - Example pass-through metrics vars.
  - Dependencies: Use the same knobs in your root `dbt_project.yml` when reusing the integration seed names.

- `integration_tests/packages.yml` and `integration_tests/requirements.txt`
  - How it helps: Ensures the right macro packages are available for tests/builds.
  - Guides: Version alignment for local validation; mirror if you test in a separate environment.
  - Dependencies: Keep versions compatible with the main `packages.yml`.

### Project config

- `dbt_project.yml` (root)
  - How it helps: Declares model materializations, default build schema (`+schema: amazon_ads_source`), and exposure of source relations via vars.
  - Guides: Set `amazon_ads_schema` (and database if needed) to where seeds are built; or build seeds into the default schema that the source expects.
  - Dependencies: Materialization choice (views/tables) doesn’t change generation, but affects runtime. Freshness behavior comes from `src_amazon_ads.yml`.

- `packages.yml`
  - How it helps: Declares `fivetran_utils` and `dbt_utils` versions that power macros used across the models.
  - Guides: Ensure these dependencies are installed before running `dbt seed/build`.
  - Dependencies: Macro availability for `union_data`, `fill_staging_columns`, and `dbt_utils` tests.

### CI and repo meta

- `.buildkite/`, `.github/`, `.gitignore`, `LICENSE`, `CHANGELOG.md`, `README.md`
  - How it helps: Reference and CI scaffolding; `README.md` gives high-level behaviors and knobs (e.g., unioning sources, disabling `portfolio_history`).
  - Guides: Use the README to understand optional features (unioning, pass-through metrics) to decide which columns to include in seeds.
  - Dependencies: CI configs are not needed for generation, but README-driven options can affect which seeds/columns you must produce.

### Practical dependencies to honor in data generation

- Entity hierarchy and FKs
  - `profile.id` → `campaign_history.profile_id` → `ad_group_history.campaign_id` → `keyword_history.ad_group_id`, `product_ad_history.ad_group_id`
  - Reporting tables reference `campaign_id`, `ad_group_id`, and `keyword_id` consistently.
- Staging uniqueness and grain (from `stg_amazon_ads.yml`)
  - History tables unique by `[source_relation, <entity_id>, last_updated_date]`
  - Report tables unique by `[source_relation, <entity_id>, date_day]`
- Freshness and timestamps
  - `_fivetran_synced` must be a timestamp; make it recent or disable freshness in `src_amazon_ads.yml`.
- Optional tables/columns
  - `portfolio_history` can be disabled via `amazon_ads__portfolio_history_enabled`
  - Pass-through metrics only required if you set the corresponding vars
- Column order and types
  - Use `docs/catalog*.json` to order columns by `index` and to format values per adapter type

Summary
- Use `src_amazon_ads.yml` for expected source tables and required columns; `stg_*.sql` and `get_*_columns.sql` for how seeds will be consumed and validated; `stg_amazon_ads.yml` for uniqueness and required fields; `docs/catalog*.json` for types and column order; `integration_tests/seeds/*.csv` and `integration_tests/dbt_project.yml` as working patterns for filenames, identifier remaps, and seed typing.


**Step 2:** Provide 3 recommendations for how to generate fake data that meets the requirements of the goal and incorporates the most efficient use of this package's resources summarized in step 1. 

Alexa: Here are three efficient, complementary strategies to generate fake, schema-accurate seeds that work seamlessly with this package.

### 1) Template-and-amplify using integration seeds
- What: Start from `integration_tests/seeds/*.csv` as canonical templates; programmatically append rows.
- How:
  - Keep file names with `_data` suffix and set identifier vars in your root `dbt_project.yml` (see `integration_tests/dbt_project.yml`).
  - Use `docs/catalog_slim.json` (or `docs/catalog.json`) for column order (via `index`) and adapter types; write values accordingly.
  - Preserve referential integrity across `profile` → `campaign_history` → `ad_group_history` → `keyword_history`/`product_ad_history`. Then generate the daily report tables.
  - Set `_fivetran_synced` to recent timestamps or temporarily disable freshness in `models/src_amazon_ads.yml`.
- Why: Lowest effort, reuses vetted headers/enums, aligns with package expectations out of the box.

### 2) Catalog-first, schema-driven generator
- What: Build a small generator that reads seed nodes from `docs/catalog*.json` and emits fully typed CSVs.
- How:
  - Parse nodes with keys starting `seed.`; derive seed names from `node.metadata.name` (or last segment of the key).
  - Order columns by `columns.*.index`; map types (integer, double precision, date, timestamp, text) to generators and serializers.
  - Drive relationships and minimal required columns from `models/src_amazon_ads.yml`, uniqueness/grain from `models/stg_amazon_ads.yml`, and per-table datatypes from `macros/get_*_columns.sql`.
  - Write `<seed_name>.csv` and optionally mirror `+column_types` and `+quote_columns` in `dbt_project.yml` (pattern in `integration_tests/dbt_project.yml`).
- Why: Most robust and adapter-accurate; scales to all tables without hand-maintaining schemas.

### 3) Test-driven minimal dataset builder
- What: Generate the smallest coherent dataset that satisfies package tests, then scale up as needed.
- How:
  - Use `models/stg_amazon_ads.yml` to determine uniqueness keys and required fields:
    - History: unique on `[source_relation, <entity_id>, last_updated_date]`
    - Reports: unique on `[source_relation, <entity_id>, date_day]`
  - Produce:
    - A small pool: `profile` (e.g., 2–3), `campaign_history` per profile (2–4), `ad_group_history` per campaign (2–5).
    - For reports, a short date horizon (e.g., last 10–30 days) with metric invariants (impressions ≥ clicks ≥ 0; cost ≈ clicks * CPC).
  - Disable `portfolio_history` if not generating it via `amazon_ads__portfolio_history_enabled: False`.
- Why: Fast to implement and validate; ensures dbt tests pass before adding volume or extra metrics.

Key knobs to set
- Source resolution: `amazon_ads_schema`, `amazon_ads_database`, and `amazon_ads_*_identifier` (match your seed filenames).
- Optional features: `amazon_ads__portfolio_history_enabled`, pass-through metrics vars if adding extra fields to report seeds.
- Freshness: set `_fivetran_synced` recent or disable freshness in `src_amazon_ads.yml`.

- Generated data should align with:
  - Schemas/types/order from `docs/catalog*.json`
  - Required columns from `models/src_amazon_ads.yml`
  - Staging expectations/tests from `models/stg_amazon_ads.yml`
  - Column sets from `macros/get_*_columns.sql`
  - Valid enums/examples from `integration_tests/seeds/*`

- After generation: run `dbt seed` then `dbt build` to validate.

- Summary
  - Use integration seeds as templates and append (quickest).
  - Or build a catalog-driven generator for full fidelity.
  - Or start with a minimal, test-driven dataset and expand.


  ### Approach 

  Alexa: Simplest path: use the existing integration seeds as templates, map identifiers to them, and run dbt.

- Copy or reference the 11 CSVs in integration_tests/seeds/ as your seeds. Keep the _data filenames.
- In your root dbt_project.yml, map package identifiers to those filenames and point the package to the schema where seeds will land (usually your target schema). Example:
  ```yaml
  vars:
    amazon_ads_ad_group_history_identifier: "ad_group_history_data"
    amazon_ads_campaign_history_identifier: "campaign_history_data"
    amazon_ads_ad_group_level_report_identifier: "ad_group_level_report_data"
    # ...repeat for all 11 identifiers...
    amazon_ads_schema: "{{ target.schema }}"
  seeds:
    +quote_columns: "{{ true if target.type == 'redshift' else false }}"
    # Optionally add +column_types mirroring integration_tests/dbt_project.yml for strict adapters
  ```
- Run:
  - dbt seed
  - dbt build -s amazon_ads_source
- If you plan to run source freshness, make _fivetran_synced recent in each CSV (or skip freshness runs).
- To expand data, append rows to these CSVs:
  - Preserve FKs: profile → campaign_history → ad_group_history → keyword/product_ad_history; reports must reference valid campaign_id/ad_group_id/keyword_id.
  - Keep report metrics coherent: impressions ≥ clicks ≥ 0; cost ≈ clicks * CPC; purchases_30_d ≤ clicks; sales_30_d ≥ 0.

Summary
- Reuse integration seeds; map identifiers in your root config; seed and build.
- Update _fivetran_synced if using freshness.
- Append more fake data later, maintaining FKs and metric rules.