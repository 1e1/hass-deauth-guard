# Deauth Guard (Home Assistant custom integration)

**Deauth Guard** (`deauth_guard`) is a [Home Assistant](https://www.home-assistant.io/) custom integration for **defensive awareness** of activity consistent with **802.11 deauthentication** frames, using a system that has a separate **Ethernet** uplink and a **WiFi** interface usable for monitor-mode capture (future releases).

- **Back-office (current)**: config flow, bus events (`deauth_guard_attack`), bounded on-disk history, services, and a status sensor. **Simulation mode** is enabled by default for safe testing.
- **GUI**: deferred (a simple control panel may follow later).

**Documentation (English only)**

- [User manual](docs/USER.md) — install, services, events, limitations.
- [Developer manual](docs/DEVELOPER.md) — architecture, APIs, extension points.
- [Open decisions](docs/DECISIONS.md) — packaging, capture stack, and privileges; **maintainer choices** required before the “real” sniffer ships.

**Similar projects (non-exhaustive)**

- [TECH7Fox/deauth-detector-hass-addons](https://github.com/TECH7Fox/deauth-detector-hass-addons) — Home Assistant **add-on** approach (Docker), different from a pure `custom_components` integration.
- [SpacehuhnTech/DeauthDetector](https://github.com/SpacehuhnTech/DeauthDetector) — embedded LED detector (ESP8266), often paired with Home Assistant over MQTT, not a Core integration.
- [deauthalyzer](https://github.com/z0m31en7/deauthalyzer) / various Scapy tools — stand-alone Linux scripts, not first-class Home Assistant entries.

**Install (manual copy)**

1. Copy `custom_components/deauth_guard/` into your Home Assistant configuration directory: `config/custom_components/deauth_guard/`.
2. Restart Home Assistant.
3. **Settings → Devices & services → Add integration → Deauth Guard** (or search by domain `deauth_guard`).

HACS support may be added in a follow-up (metadata, validation).

**Translations:** `translations/en.json` and **`translations/fr.json`** for the config flow, services, and entity names (UI language follows the Home Assistant user profile).

**Tests:** `pip install -r requirements-dev.txt` then `python -m pytest tests/ -v` (uses lightweight `homeassistant` stubs in `tests/ha_stubs.py`; no full HA wheel required).

**HACS / hassfest:** the repo includes `hacs.json`, `custom_components/deauth_guard/brand/icon.png`, and GitHub Actions **Validate** (hassfest + HACS). To run **hassfest locally with Docker** (e.g. on another machine), see [Developer manual — Running hassfest locally with Docker](docs/DEVELOPER.md#running-hassfest-locally-with-docker). For the default HACS store, also add a **GitHub Release**, **repository description**, **topics**, and enable **issues** (see [HACS include](https://hacs.xyz/docs/publish/include)).

**License:** see `LICENSE` (intended: MIT; adjust to match your preference before publishing).

**Disclaimer:** use only on **networks you are authorized to monitor** and in compliance with applicable law. This software does not replace a professional WIDS; it is intended for home automation and lab use.

## Raspberry Pi 3B

The integration is designed to be **lightweight** (bounded history, no hot-path busy loops). A **real** 802.11 stack on a Pi 3B still requires a suitable **adapter and driver** and careful resource tuning; see the developer manual.
