from __future__ import annotations

import pytest

from sp_models.entities.campaigns import CampaignSP, SP_CAMPAIGNS_ENUMS


def test_campaign_defaults_and_enum_validation():
    camp = CampaignSP(
        campaign_id="cmp_1",
        account_id="acc_1",
        name="Test Campaign",
    )
    assert camp.ad_product == "SPONSORED_PRODUCTS"
    assert camp.state in SP_CAMPAIGNS_ENUMS["state"]
    assert camp.creation_datetime
    assert camp.last_updated_datetime


@pytest.mark.parametrize("state", SP_CAMPAIGNS_ENUMS["state"])  # allowed
def test_campaign_valid_states(state: str):
    camp = CampaignSP(
        campaign_id="cmp_2",
        account_id="acc_1",
        name="C",
        state=state,
    )
    assert camp.state == state


def test_campaign_invalid_state_raises():
    with pytest.raises(ValueError):
        CampaignSP(
            campaign_id="cmp_bad",
            account_id="acc",
            name="C",
            state="INVALID",
        )


@pytest.mark.parametrize("targeting_type", SP_CAMPAIGNS_ENUMS["targeting_type"])  # allowed
def test_campaign_valid_targeting_type(targeting_type: str):
    camp = CampaignSP(
        campaign_id="cmp_3",
        account_id="acc_1",
        name="C",
        targeting_type=targeting_type,
    )
    assert camp.targeting_type == targeting_type


def test_campaign_invalid_targeting_type_raises():
    with pytest.raises(ValueError):
        CampaignSP(
            campaign_id="cmp_bad2",
            account_id="acc",
            name="C",
            targeting_type="WRONG",
        )


