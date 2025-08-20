from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Dict, Iterable, Iterator, List

try:
    from ..seed_core import utc_ts, daterange
except Exception:
    from scripts.seed_core import utc_ts, daterange  # type: ignore


def _metrics() -> Dict[str, float]:
    clicks = max(0, int(random.gauss(3, 5)))
    impressions = max(clicks, clicks + int(abs(random.gauss(20, 50))))
    cpc = random.uniform(0.3, 1.5)
    cost = round(clicks * cpc, 2)
    purchases = max(0, min(clicks, int(random.gauss(1, 2))))
    sales = round(purchases * random.uniform(10, 100), 2)
    return {
        "clicks": clicks,
        "impressions": impressions,
        "cost": cost,
        "purchases_30_d": purchases,
        "sales_30_d": sales,
    }


def generate_campaign_level(parent_campaign_ids: List[str], days: int) -> Iterator[dict]:
    for cid in parent_campaign_ids:
        for d in daterange(days):
            m = _metrics()
            yield {
                "campaign_id": cid,
                "date": d.strftime("%Y-%m-%d"),
                "_fivetran_synced": utc_ts(),
                "campaign_applicable_budget_rule_id": "",
                "campaign_applicable_budget_rule_name": "",
                "campaign_bidding_strategy": random.choice(["optimizeForSales", "autoForSales", "manual"]),
                "campaign_budget_amount": round(random.uniform(100, 5000), 2),
                "campaign_budget_currency_code": "USD",
                "campaign_budget_type": random.choice(["DAILY_BUDGET", "LIFETIME_BUDGET"]),
                **m,
                "campaign_rule_based_budget_amount": "",
            }



def generate_ad_group_level(parent_ad_group_ids: List[str], days: int) -> Iterator[dict]:
    for ad_group_id in parent_ad_group_ids:
        for d in daterange(days):
            m = _metrics()
            yield {
                "ad_group_id": ad_group_id,
                "date": d.strftime("%Y-%m-%d"),
                "_fivetran_synced": utc_ts(),
                "campaign_bidding_strategy": random.choice(["optimizeForSales", "autoForSales", "manual"]),
                **m,
            }


def generate_advertised_product(parent_ad_group_ids: List[str], days: int) -> Iterator[dict]:
    next_ad_id = 7000
    for ad_group_id in parent_ad_group_ids:
        for d in daterange(days):
            m = _metrics()
            ad_id = str(next_ad_id)
            next_ad_id += 1
            yield {
                "ad_id": ad_id,
                "ad_group_id": ad_group_id,
                "date": d.strftime("%Y-%m-%d"),
                "_fivetran_synced": utc_ts(),
                "advertised_asin": f"B0{random.randint(1000000, 9999999)}",
                "advertised_sku": f"SKU-{ad_id}",
                **m,
            }


def generate_search_term_ad_keyword(parent_ad_group_ids: List[str], days: int) -> Iterator[dict]:
    next_keyword_id = 8000
    for ad_group_id in parent_ad_group_ids:
        for d in daterange(days):
            m = _metrics()
            keyword_id = str(next_keyword_id)
            next_keyword_id += 1
            base_kw = f"kw_{keyword_id}"
            yield {
                "ad_group_id": ad_group_id,
                "keyword_id": keyword_id,
                "date": d.strftime("%Y-%m-%d"),
                "_fivetran_synced": utc_ts(),
                "keyword_text": base_kw,
                "search_term": f"search_{base_kw}",
                "match_type": random.choice(["BROAD", "PHRASE", "EXACT"]),
                **m,
            }


def generate_targeting_keyword(parent_ad_group_ids: List[str], days: int) -> Iterator[dict]:
    next_keyword_id = 9000
    for ad_group_id in parent_ad_group_ids:
        for d in daterange(days):
            m = _metrics()
            keyword_id = str(next_keyword_id)
            next_keyword_id += 1
            yield {
                "ad_group_id": ad_group_id,
                "keyword_id": keyword_id,
                "date": d.strftime("%Y-%m-%d"),
                "_fivetran_synced": utc_ts(),
                "keyword_text": f"kw_{keyword_id}",
                "match_type": random.choice(["BROAD", "PHRASE", "EXACT"]),
                "bid": round(random.uniform(0.2, 3.0), 2),
                **m,
            }



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