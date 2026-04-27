"""Structure checks for `synthetic_channel_band_phy` (no Home Assistant)."""

from __future__ import annotations

import random

import pytest

from custom_components.deauth_guard.const import BAND_2_4_GHZ, BAND_5_GHZ, BAND_6_GHZ
from custom_components.deauth_guard.rf_synthetic import synthetic_channel_band_phy


@pytest.mark.parametrize("seed", range(10))
def test_synthetic_channel_band_phy_shape_and_ranges(seed: int) -> None:
    random.seed(seed)
    for _ in range(20):
        d = synthetic_channel_band_phy()
        assert "channel" in d and "band" in d and "wifi_phy" in d
        assert isinstance(d["channel"], int)
        assert d["band"] in (BAND_2_4_GHZ, BAND_5_GHZ, BAND_6_GHZ)
        assert isinstance(d["wifi_phy"], str)
        if d["band"] == BAND_2_4_GHZ:
            assert 1 <= d["channel"] <= 11
        elif d["band"] == BAND_5_GHZ:
            assert d["channel"] in (
                36,
                40,
                44,
                48,
                52,
                100,
                116,
                120,
                149,
                153,
                157,
                161,
                165,
            )
        else:
            assert d["band"] == BAND_6_GHZ
            assert d["channel"] in (1, 5, 9, 13, 21, 45, 101, 165, 201)
