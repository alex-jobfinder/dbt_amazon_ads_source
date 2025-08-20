from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

try:
    from ..seed_core import utc_ts
except Exception:
    from scripts.seed_core import utc_ts  # type: ignore


def generate_profiles(n: int) -> List[dict]:
    rows: List[dict] = []
    start_id = 1000
    for i in range(n):
        pid = str(start_id + i)
        rows.append({
            "id": pid,
            "_fivetran_synced": utc_ts(),
            "account_id": f"acct-{pid}",
            "account_marketplace_string_id": "ATVPDKIKX0DER",
            "account_name": f"Profile {pid}",
            "country_code": "US",
            "currency_code": "USD",
            "creation_date": utc_ts(),
            "last_updated_date": utc_ts(),
        })
    return rows


def generate_campaign_history(parent_profile_ids: List[str], n: int) -> List[dict]:
    rows: List[dict] = []
    start_id = 2000
    for i in range(n):
        cid = str(start_id + i)
        profile_id = random.choice(parent_profile_ids) if parent_profile_ids else "1000"
        start_dt = (date.today() - timedelta(days=random.randint(10, 100))).strftime("%Y-%m-%d")
        rows.append({
            "id": cid,
            "profile_id": profile_id,
            "name": f"Campaign {cid}",
            "bidding_strategy": random.choice(["autoForSales", "manual", "legacyForSales"]),
            "budget": round(random.uniform(10, 1000), 2),
            "budget_type": random.choice(["daily", "lifetime"]),
            "effective_budget": "",
            "start_date": start_dt,
            "end_date": "",
            "serving_status": random.choice(["CAMPAIGN_STATUS_ENABLED", "CAMPAIGN_PAUSED"]),
            "state": random.choice(["enabled", "paused", "archived"]),
            "targeting_type": random.choice(["manual", "auto"]),
            "creation_date": utc_ts(),
            "last_updated_date": utc_ts(),
            "_fivetran_synced": utc_ts(),
        })
    return rows


def generate_ad_group_history(parent_campaign_ids: List[str], n: int) -> List[dict]:
    rows: List[dict] = []
    start_id = 3000
    for i in range(n):
        aid = str(start_id + i)
        cid = random.choice(parent_campaign_ids) if parent_campaign_ids else "2000"
        rows.append({
            "id": aid,
            "campaign_id": cid,
            "name": f"AdGroup {aid}",
            "default_bid": round(random.uniform(0.2, 5.0), 2),
            "serving_status": random.choice(["AD_GROUP_STATUS_ENABLED", "CAMPAIGN_PAUSED"]),
            "state": random.choice(["enabled", "paused", "archived"]),
            "creation_date": utc_ts(),
            "last_updated_date": utc_ts(),
            "_fivetran_synced": utc_ts(),
        })
    return rows


def generate_keyword_history(parent_ag_ids: List[str], parent_camp_ids: List[str], n: int) -> List[dict]:
    rows: List[dict] = []
    start_id = 4000
    for i in range(n):
        kid = str(start_id + i)
        agid = random.choice(parent_ag_ids) if parent_ag_ids else "3000"
        cid = random.choice(parent_camp_ids) if parent_camp_ids else "2000"
        rows.append({
            "id": kid,
            "ad_group_id": agid,
            "campaign_id": cid,
            "keyword_text": f"kw_{kid}",
            "match_type": random.choice(["BROAD", "PHRASE", "EXACT"]),
            "native_language_keyword": f"kw_{kid}",
            "native_language_locale": "en_US",
            "serving_status": random.choice(["ENABLED", "PAUSED"]),
            "state": random.choice(["enabled", "paused", "archived"]),
            "bid": round(random.uniform(0.2, 3.0), 2),
            "creation_date": utc_ts(),
            "last_updated_date": utc_ts(),
            "_fivetran_synced": utc_ts(),
        })
    return rows


def generate_product_ad_history(parent_ag_ids: List[str], parent_camp_ids: List[str], n: int) -> List[dict]:
    rows: List[dict] = []
    start_id = 5000
    for i in range(n):
        pid = str(start_id + i)
        agid = random.choice(parent_ag_ids) if parent_ag_ids else "3000"
        cid = random.choice(parent_camp_ids) if parent_camp_ids else "2000"
        rows.append({
            "id": pid,
            "ad_group_id": agid,
            "campaign_id": cid,
            "asin": f"B0{random.randint(1000000, 9999999)}",
            "sku": f"SKU-{pid}",
            "serving_status": random.choice(["ENABLED", "PAUSED"]),
            "state": random.choice(["enabled", "paused", "archived"]),
            "creation_date": utc_ts(),
            "last_updated_date": utc_ts(),
            "_fivetran_synced": utc_ts(),
        })
    return rows


def generate_portfolio_history(parent_campaign_ids: List[str], n: int) -> List[dict]:
    rows: List[dict] = []
    start_id = 6000
    for i in range(n):
        pid = str(start_id + i)
        cid = random.choice(parent_campaign_ids) if parent_campaign_ids else "2000"
        rows.append({
            "id": pid,
            "campaign_id": cid,
            "name": f"Portfolio {pid}",
            "creation_date": utc_ts(),
            "last_updated_date": utc_ts(),
            "_fivetran_synced": utc_ts(),
        })
    return rows




"""

INSERT INTO schema_metadata VALUES ('PROFILE', '_fivetran_id',                  'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'profile_id',                    'INTEGER', 0, 1,    'PROFILE',          'profile_id');
INSERT INTO schema_metadata VALUES ('PROFILE', 'asin',                          'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'estimated_impression_lower',    'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'estimated_impression_upper',    'REAL',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'strategy',                      'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'targeting_type',                'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PROFILE', 'theme',                         'TEXT',    0, 0,    NULL,               NULL);




INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'id',                   'INTEGER', 1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'last_updated_date',    'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'ad_group_id',          'INTEGER', 0, 1, 'AD_GROUP_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'campaign_id',          'INTEGER', 0, 1, 'CAMPAIGN_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'bid',                  'REAL',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'creation_date',        'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'keyword_text',         'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'match_type',           'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'native_language_keyword','TEXT',  0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'native_language_locale','TEXT',   0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'serving_status',       'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_HISTORY',         'state',                'TEXT',    0, 0, NULL,               NULL);


INSERT INTO schema_metadata VALUES ('PRODUCT_AD_HISTORY',        'name',                 'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_HISTORY',        'product_ad_id',        'INTEGER', 1, 1, 'PRODUCT_AD_HISTORY','product_ad_id');
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_HISTORY',        'help_url',             'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PRODUCT_AD_HISTORY',        'message',              'TEXT',    0, 0, NULL,               NULL);


INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'id',                   'INTEGER', 1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'last_updated_date',    'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'portfolio_id',         'INTEGER', 0, 1, 'PORTFOLIO_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'bidding_strategy',     'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'budget',               'REAL',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'effective_budget',     'REAL',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'budget_type',          'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'creation_date',        'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'end_date',             'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'name',                 'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'profile_id',           'INTEGER', 0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'serving_status',       'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'start_date',           'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'state',                'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_HISTORY',         'targeting_type',       'TEXT',    0, 0, NULL,               NULL);



INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'id',                   'INTEGER', 1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'last_updated_date',    'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'campaign_id',          'INTEGER', 0, 1, 'CAMPAIGN_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'ad_group_id',          'INTEGER', 0, 1, 'AD_GROUP_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'creation_date',        'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'keyword_text',         'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'match_type',           'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'native_language_keyword','TEXT',  0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'native_language_locale','TEXT',   0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'serving_status',       'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('KEYWORD_HISTORY',          'state',                'TEXT',    0, 0, NULL,               NULL);



INSERT INTO schema_metadata VALUES ('PORTFOLIO_HISTORY', 'date',        'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PORTFOLIO_HISTORY', 'campaign_id','INTEGER', 1, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('PORTFOLIO_HISTORY', '_metrics',    'TEXT',    0, 0,    NULL,               NULL);





INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_HISTORY', 'name',      'TEXT',    1, 0,    NULL,                        NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_HISTORY', 'target_id','INTEGER', 1, 1,    'TARGETING_CLAUSE_HISTORY','target_id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_HISTORY', 'help_url', 'TEXT',    0, 0,    NULL,                        NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_NEGATIVE_KEYWORD_HISTORY', 'level',    'TEXT',    0, 0,    NULL,                        NULL);


INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_HISTORY', 'name',                 'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_HISTORY', 'keyword_id',           'INTEGER', 1, 1, 'KEYWORD_HISTORY',   'id');
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_HISTORY', 'help_url',             'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_KEYWORD_HISTORY', 'message',              'TEXT',    0, 0, NULL,               NULL);

INSERT INTO schema_metadata VALUES ('TARGETING_CLAUSE_HISTORY', '_fivetran_id',        'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_CLAUSE_HISTORY', 'target_id',           'INTEGER', 0, 1, 'TARGETING_CLAUSE_HISTORY','target_id');
INSERT INTO schema_metadata VALUES ('TARGETING_CLAUSE_HISTORY', 'type',                'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_CLAUSE_HISTORY', 'value',               'TEXT',    0, 0, NULL,               NULL);


INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'id',                                 'INTEGER', 1, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'budget_increase_by_type',           'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'budget_increase_by_value',          'REAL',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'created_date',                      'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'date_range_type_duration_end_date',   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'date_range_type_duration_start_date', 'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'event_type_rule_duration_end_date',   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'event_type_rule_duration_event_id',   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'event_type_rule_duration_event_name', 'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'event_type_rule_duration_start_date', 'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'last_updated_date',                  'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'name',                              'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'preformance_measure_comparison_operator', 'TEXT', 0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'preformance_measure_metric_name',   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'preformance_measure_treshold',      'REAL',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'recurrence_type',                   'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'state',                             'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'status',                            'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('NEGATIVE_TARGETING_CLAUSE_HISTORY', 'type',                              'TEXT',    0, 0, NULL, NULL);














INSERT INTO schema_metadata VALUES ('CAMPAIGN_LEVEL_REPORT', 'date',      'TEXT',    1, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_LEVEL_REPORT', 'placement', 'TEXT',    1, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_LEVEL_REPORT', '_metrics',  'TEXT',    0, 0, NULL, NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_REPORT', 'date',       'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_REPORT', 'ad_group_id','INTEGER', 1, 1, 'AD_GROUP_HISTORY',   'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_REPORT', 'campaign_id','INTEGER', 1, 1, 'CAMPAIGN_HISTORY',   'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_REPORT', 'keyword_id','INTEGER',  1, 1, 'KEYWORD_HISTORY',    'id');
INSERT INTO schema_metadata VALUES ('CAMPAIGN_PLACEMENT_REPORT', '_metrics',   'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', 'date',       'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', 'search_term','TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', 'ad_group_id','INTEGER', 1, 1,    'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', 'campaign_id','INTEGER', 1, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', 'keyword_id','INTEGER',  1, 1,    'KEYWORD_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('TARGETING_KEYWORD_REPORT', '_metrics',   'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_AD_KEYWORD_REPORT', 'date',       'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_AD_KEYWORD_REPORT', 'ad_group_id','INTEGER', 1, 1, 'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_AD_KEYWORD_REPORT', '_metrics',   'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_LEVEL_REPORT', 'date',        'TEXT',    1, 0, NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('AD_GROUP_LEVEL_REPORT', 'ad_id',       'INTEGER', 1, 1, 'PRODUCT_AD_HISTORY',         'product_ad_id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_LEVEL_REPORT', 'ad_group_id', 'INTEGER', 1, 1, 'AD_GROUP_HISTORY',           'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_LEVEL_REPORT', 'campaign_id', 'INTEGER', 1, 1, 'CAMPAIGN_HISTORY',           'id');
INSERT INTO schema_metadata VALUES ('AD_GROUP_LEVEL_REPORT', '_metrics',    'TEXT',    0, 0, NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', 'date',         'TEXT',    1, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', 'purchased_asin','TEXT',    1, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', 'ad_group_id',   'INTEGER', 1, 1, 'AD_GROUP_HISTORY','id');
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', 'campaign_id',   'INTEGER', 1, 1, 'CAMPAIGN_HISTORY','id');
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', 'keyword_id',    'INTEGER', 1, 1, 'KEYWORD_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('ADVERTISED_PRODUCT_REPORT', '_metrics',      'TEXT',    0, 0, NULL,             NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_KEYWORD_REPORT', 'date',        'TEXT',    1, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_KEYWORD_REPORT', 'search_term','TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_KEYWORD_REPORT', 'ad_group_id','INTEGER', 1, 1, 'AD_GROUP_HISTORY','id');
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_KEYWORD_REPORT', 'campaign_id','INTEGER', 1, 1, 'CAMPAIGN_HISTORY','id');
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_KEYWORD_REPORT', '_metrics',   'TEXT',    0, 0, NULL,               NULL);
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_TARGETING_REPORT', 'date',       'TEXT',    1, 0,    NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_TARGETING_REPORT', 'ad_group_id','INTEGER', 1, 1,    'AD_GROUP_HISTORY',           'id');
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_TARGETING_REPORT', 'campaign_id','INTEGER', 1, 1,    'CAMPAIGN_HISTORY',           'id');
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_TARGETING_REPORT', 'keyword_id','INTEGER', 1, 1,    'TARGETING_EXPRESSION',       'target_id');
INSERT INTO schema_metadata VALUES ('SEARCH_TERM_TARGETING_REPORT', '_metrics',  'TEXT',    0, 0,    NULL,                         NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', 'date',          'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', 'purchased_asin','TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', 'ad_group_id',   'INTEGER', 1, 1,    'AD_GROUP_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', 'campaign_id',   'INTEGER', 1, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', 'keyword_id',    'INTEGER', 1, 1,    'KEYWORD_HISTORY',  'id');
INSERT INTO schema_metadata VALUES ('TARGETING_REPORT', '_metrics',      'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_TARGETING_REPORT', 'name',        'TEXT',    1, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_TARGETING_REPORT', 'campaign_id','INTEGER', 1, 1,    'CAMPAIGN_HISTORY', 'id');
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_TARGETING_REPORT', 'help_url',    'TEXT',    0, 0,    NULL,               NULL);
INSERT INTO schema_metadata VALUES ('PURCHASED_PRODUCT_TARGETING_REPORT', 'message',     'TEXT',    0, 0,    NULL,               NULL);




"""