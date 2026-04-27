"""Stdlib-only synthetic RF fields for simulation and unit tests."""

from __future__ import annotations

import random
from typing import Any

from .const import BAND_2_4_GHZ, BAND_5_GHZ, BAND_6_GHZ


def synthetic_channel_band_phy() -> dict[str, Any]:
    """Plausible (channel, band, wifi_phy) for tests; not RF-accurate."""
    band = random.choices(
        population=[BAND_2_4_GHZ, BAND_5_GHZ, BAND_6_GHZ],
        weights=(50, 40, 10),
        k=1,
    )[0]
    if band == BAND_2_4_GHZ:
        ch = random.randint(1, 11)
        phy = random.choice(("b", "g", "n", "ax"))
    elif band == BAND_5_GHZ:
        ch = random.choice(
            (36, 40, 44, 48, 52, 100, 116, 120, 149, 153, 157, 161, 165)
        )
        phy = random.choice(("a", "n", "ac", "ax"))
    else:  # 6 GHz
        ch = random.choice((1, 5, 9, 13, 21, 45, 101, 165, 201))
        phy = random.choice(("ax", "be"))
    return {"channel": ch, "band": band, "wifi_phy": phy}
