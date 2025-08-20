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


