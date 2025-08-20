from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Optional

from .base import RandomContext, random_name, uid
from ..entities.campaigns import CampaignSP, SP_CAMPAIGNS_ENUMS


def build_campaign(ctx: RandomContext, account_id: str, name: Optional[str] = None) -> CampaignSP:
    table_states = SP_CAMPAIGNS_ENUMS["state"]
    delivery_statuses = SP_CAMPAIGNS_ENUMS["delivery_status"]
    targeting_vals = SP_CAMPAIGNS_ENUMS["targeting_type"]
    recurrence_vals = SP_CAMPAIGNS_ENUMS["budget_recurrence_time_period"]

    start = date.today() - timedelta(days=ctx.rng.randint(0, 30))
    end = start + timedelta(days=ctx.rng.randint(7, 90)) if ctx.rng.random() < 0.4 else None

    return CampaignSP(
        campaign_id=uid("cmp"),
        account_id=account_id,
        portfolio_id=None,
        name=name or random_name("SP Campaign", rng=ctx.rng),
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d") if end else None,
        state=ctx.rng.choice(table_states),
        delivery_status=(ctx.rng.choice(delivery_statuses) if delivery_statuses and ctx.rng.random() < 0.6 else None),
        delivery_reasons=json.dumps(["OK"]) if ctx.rng.random() < 0.2 else None,
        serving_status=ctx.rng.choice(["SERVING", "NOT_SERVING", None]),
        targeting_type=ctx.rng.choice(targeting_vals),
        dynamic_bidding_strategy=ctx.rng.choice(["legacy", "down_only", "up_and_down", None]),
        placement_bid_adjustments=json.dumps({"TOP_OF_SEARCH": ctx.rng.randint(0, 200)}) if ctx.rng.random() < 0.3 else None,
        budget_caps_type=ctx.rng.choice(["CAMPAIGN", "PORTFOLIO", None]),
        budget_recurrence_time_period=ctx.rng.choice(recurrence_vals),
        budget_type=ctx.rng.choice(["DAILY", "LIFETIME"]),
        budget_amount=round(ctx.rng.uniform(10, 500), 2),
        budget_effective_amount=None,
        budget_currency=ctx.rng.choice(["USD", "CAD", "EUR"]),
        tags=json.dumps([{ "key": "env", "value": ctx.rng.choice(["test", "prod", "stage"]) }]) if ctx.rng.random() < 0.25 else None,
        brand_entity_id=None,
        extras=None,
    )


