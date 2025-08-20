from __future__ import annotations

import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


from ..enums import SP_CAMPAIGNS_ENUMS


# ------------------------------------------------------------
# Exact DDL for sp_campaigns (table + enum validation triggers)
# ------------------------------------------------------------
SP_CAMPAIGNS_DDL: str = """
CREATE TABLE IF NOT EXISTS sp_campaigns (
    campaign_id                    TEXT PRIMARY KEY,
    account_id                     TEXT NOT NULL,
    portfolio_id                   TEXT,

    ad_product                     TEXT NOT NULL DEFAULT 'SPONSORED_PRODUCTS' CHECK (ad_product = 'SPONSORED_PRODUCTS'),
    name                           TEXT NOT NULL,

    start_date                     TEXT,
    end_date                       TEXT,

    state                          TEXT NOT NULL CHECK (state IN ('ENABLED','PAUSED','ARCHIVED')),
    delivery_status                TEXT,
    delivery_reasons               TEXT,
    serving_status                 TEXT,

    targeting_type                 TEXT,

    dynamic_bidding_strategy       TEXT,
    placement_bid_adjustments      TEXT,

    budget_caps_type               TEXT,
    budget_recurrence_time_period  TEXT,
    budget_type                    TEXT CHECK (budget_type IN ('DAILY','LIFETIME')),
    budget_amount                  REAL,
    budget_effective_amount        REAL,
    budget_currency                TEXT,

    tags                           TEXT,

    creation_datetime              TEXT,
    last_updated_datetime          TEXT,

    brand_entity_id                TEXT,
    extras                         TEXT
);
CREATE INDEX IF NOT EXISTS idx_sp_campaigns_account   ON sp_campaigns(account_id);
CREATE INDEX IF NOT EXISTS idx_sp_campaigns_portfolio ON sp_campaigns(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_sp_campaigns_state     ON sp_campaigns(state);

DROP TRIGGER IF EXISTS trg_sp_campaigns_validate_enums_ins;
DROP TRIGGER IF EXISTS trg_sp_campaigns_validate_enums_upd;

CREATE TRIGGER IF NOT EXISTS trg_sp_campaigns_validate_enums_ins
BEFORE INSERT ON sp_campaigns
FOR EACH ROW
BEGIN
    -- ad_product
    SELECT CASE
        WHEN NEW.ad_product IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM enums_table
            WHERE enum_name = 'ad_product'
              AND enum_value = NEW.ad_product
              AND enum_ad_product = NEW.ad_product
        ) THEN RAISE(ABORT, 'sp_campaigns.ad_product not in enums_table')
    END;

    -- state
    SELECT CASE
        WHEN NEW.state IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM enums_table
            WHERE enum_name = 'state'
              AND enum_ad_product = NEW.ad_product
              AND enum_value = NEW.state
        ) THEN RAISE(ABORT, 'sp_campaigns.state not valid for ad_product')
    END;

    -- delivery_status
    SELECT CASE
        WHEN NEW.delivery_status IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM enums_table
            WHERE enum_name = 'delivery_status'
              AND enum_ad_product = NEW.ad_product
              AND enum_value = NEW.delivery_status
        ) THEN RAISE(ABORT, 'sp_campaigns.delivery_status not valid for ad_product')
    END;

    -- targeting_type
    SELECT CASE
        WHEN NEW.targeting_type IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM enums_table
            WHERE enum_name = 'targeting_settings'
              AND enum_ad_product = NEW.ad_product
              AND enum_value = NEW.targeting_type
        ) THEN RAISE(ABORT, 'sp_campaigns.targeting_type not valid for ad_product')
    END;

    -- budget_recurrence_time_period
    SELECT CASE
        WHEN NEW.budget_recurrence_time_period IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM enums_table
            WHERE enum_name = 'recurrence_time_period'
              AND enum_ad_product = NEW.ad_product
              AND enum_value = NEW.budget_recurrence_time_period
        ) THEN RAISE(ABORT, 'sp_campaigns.budget_recurrence_time_period not valid for ad_product')
    END;
END;

CREATE TRIGGER IF NOT EXISTS trg_sp_campaigns_validate_enums_upd
BEFORE UPDATE ON sp_campaigns
FOR EACH ROW
BEGIN
    -- ad_product
    SELECT CASE
        WHEN NEW.ad_product IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM enums_table
            WHERE enum_name = 'ad_product'
              AND enum_value = NEW.ad_product
              AND enum_ad_product = NEW.ad_product
        ) THEN RAISE(ABORT, 'sp_campaigns.ad_product not in enums_table')
    END;

    -- state
    SELECT CASE
        WHEN NEW.state IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM enums_table
            WHERE enum_name = 'state'
              AND enum_ad_product = NEW.ad_product
              AND enum_value = NEW.state
        ) THEN RAISE(ABORT, 'sp_campaigns.state not valid for ad_product')
    END;

    -- delivery_status
    SELECT CASE
        WHEN NEW.delivery_status IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM enums_table
            WHERE enum_name = 'delivery_status'
              AND enum_ad_product = NEW.ad_product
              AND enum_value = NEW.delivery_status
        ) THEN RAISE(ABORT, 'sp_campaigns.delivery_status not valid for ad_product')
    END;

    -- targeting_type
    SELECT CASE
        WHEN NEW.targeting_type IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM enums_table
            WHERE enum_name = 'targeting_settings'
              AND enum_ad_product = NEW.ad_product
              AND enum_value = NEW.targeting_type
        ) THEN RAISE(ABORT, 'sp_campaigns.targeting_type not valid for ad_product')
    END;

    -- budget_recurrence_time_period
    SELECT CASE
        WHEN NEW.budget_recurrence_time_period IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM enums_table
            WHERE enum_name = 'recurrence_time_period'
              AND enum_ad_product = NEW.ad_product
              AND enum_value = NEW.budget_recurrence_time_period
        ) THEN RAISE(ABORT, 'sp_campaigns.budget_recurrence_time_period not valid for ad_product')
    END;
END;
"""


def utc_now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class CampaignSP(BaseModel):
    campaign_id: str
    account_id: str
    portfolio_id: Optional[str] = None
    name: str

    # Dates
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    # Enums and state
    ad_product: str = Field(default="SPONSORED_PRODUCTS")
    state: str = Field(default="ENABLED")
    delivery_status: Optional[str] = None
    delivery_reasons: Optional[str] = None
    serving_status: Optional[str] = None
    targeting_type: Optional[str] = None

    # Bidding/Budgeting
    dynamic_bidding_strategy: Optional[str] = None
    placement_bid_adjustments: Optional[str] = None
    budget_caps_type: Optional[str] = None
    budget_recurrence_time_period: Optional[str] = None
    budget_type: Optional[str] = None
    budget_amount: Optional[float] = None
    budget_effective_amount: Optional[float] = None
    budget_currency: Optional[str] = None

    # Timestamps
    creation_datetime: str = Field(default_factory=utc_now_iso)
    last_updated_datetime: str = Field(default_factory=utc_now_iso)

    # Misc
    tags: Optional[str] = None
    brand_entity_id: Optional[str] = None
    extras: Optional[str] = None

    # Validators
    @validator("ad_product")
    def _validate_ad_product(cls, value: str) -> str:
        allowed = SP_CAMPAIGNS_ENUMS["ad_product"]
        if value not in allowed:
            raise ValueError(f"ad_product must be one of {allowed}")
        return value

    @validator("state")
    def _validate_state(cls, value: str) -> str:
        allowed = SP_CAMPAIGNS_ENUMS["state"]
        if value not in allowed:
            raise ValueError(f"state must be one of {allowed}")
        return value

    @validator("delivery_status")
    def _validate_delivery_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = SP_CAMPAIGNS_ENUMS["delivery_status"]
        if value not in allowed:
            raise ValueError(f"delivery_status must be one of {allowed}")
        return value

    @validator("targeting_type")
    def _validate_targeting_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = SP_CAMPAIGNS_ENUMS["targeting_type"]
        if value not in allowed:
            raise ValueError(f"targeting_type must be one of {allowed}")
        return value

    @validator("budget_recurrence_time_period")
    def _validate_budget_recurrence_time_period(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = SP_CAMPAIGNS_ENUMS["budget_recurrence_time_period"]
        if value not in allowed:
            raise ValueError(f"budget_recurrence_time_period must be one of {allowed}")
        return value

    @validator("budget_type")
    def _validate_budget_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = SP_CAMPAIGNS_ENUMS["budget_type"]
        if value not in allowed:
            raise ValueError(f"budget_type must be one of {allowed}")
        return value


__all__ = [
    "CampaignSP",
    "SP_CAMPAIGNS_ENUMS",
    "SP_CAMPAIGNS_DDL",
]


