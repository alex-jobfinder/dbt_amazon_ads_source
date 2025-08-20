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


