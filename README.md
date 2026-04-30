# Deauth Guard

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=agerlier&repository=ha-deauth&category=integration)
[![GitHub release](https://img.shields.io/github/v/release/agerlier/ha-deauth?style=flat-square)](https://github.com/agerlier/ha-deauth/releases)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/agerlier/ha-deauth?style=flat-square&color=brightgreen)](https://github.com/agerlier/ha-deauth/commits/main)
[![License](https://img.shields.io/github/license/agerlier/ha-deauth?style=flat-square)](https://github.com/agerlier/ha-deauth/blob/main/LICENSE)

**Defensive awareness of 802.11 deauthentication-style activity in Home Assistant** — for hosts with a separate Ethernet uplink and a Wi‑Fi radio you can dedicate to monitor mode when capture lands in a future release.

Today you get a full **config flow** (one entry, up to **three** Wi‑Fi source slots with per-radio channel filters), **`deauth_guard_attack`** bus events, **bounded on-disk history**, **services**, and a **status** sensor. **Simulation** is the default so you can develop automations without hardware.

---

## ✨ Features

- 📡 **802.11 deauth awareness** — surface patterns consistent with deauthentication frames for automations (notifications, logging, countermeasures you design).
- 🎛️ **Up to three radios** — Radio 1 required; Radio 2 and 3 optional; per-radio **channel multi-select** (empty = no software filter on that interface).
- 🧪 **Simulation first** — synthetic events on a timer; no adapter required for tests.
- 🔔 **Alert rules** — up to two optional sliding-window rules (min count + window seconds); channel filter + rules gate when **`deauth_guard_attack`** fires (not every history row).
- 📚 **Bounded history** — ring buffer on disk for dashboards and **`deauth_guard.get_history`**.
- 🛠️ **Services** — `deauth_guard.get_history`, `deauth_guard.clear_history`.
- 🖥️ **Config UI** — single config entry; reconfigure from the integration card.
- 🌍 **EN / FR** — config flow, services, and entity strings (`translations/en.json`, `translations/fr.json`); UI language follows the HA user profile.
- 🍓 **Pi-friendly** — designed to stay lightweight (bounded buffers, no hot-path busy loops on the main thread).

---

## 🚀 Installation

### Via HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=agerlier&repository=ha-deauth&category=integration)

1. Click the button above **or** open HACS → Integrations → ⋮ → **Custom repositories**
2. Add `https://github.com/agerlier/ha-deauth` as **Integration**
3. Install **Deauth Guard**
4. Restart Home Assistant

### Manual

1. Copy `custom_components/deauth_guard/` from this repository into your Home Assistant configuration directory so you have `config/custom_components/deauth_guard/…`
2. Restart Home Assistant

---

## ⚙️ Setup

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=deauth_guard)

1. Click the button above **or** go to **Settings → Devices & services → Add integration**
2. Search for **Deauth Guard** (domain `deauth_guard`)
3. Complete the wizard: radios (simulation or future real interfaces), channels per radio, simulation interval, history size, alert rules

Re-open **Configure** on the integration card anytime to change options.

> [!NOTE]
> **Real** monitor-mode capture is prepared in configuration but not fully shipped yet; see [Open decisions](docs/DECISIONS.md) for capture stack and privilege choices.

---

## 📡 Events & automations

Subscribe to **`deauth_guard_attack`** when the alert policy allows an emit. Payloads favor **structured fields** (normalized MACs, reason codes, RSSI, 802.11 channel, band labels like `2.4 GHz` / `5 GHz` / `6 GHz`, optional `wifi_phy`, `emit`).

Example trigger shape (adapt `event_data` to your instance):

```yaml
triggers:
  - trigger: event
    event_type: deauth_guard_attack
```

Full field list and behavior (first detection vs sliding windows, simulation quirks) → **[User manual — Events](docs/USER.md)**.

---

## 🛠️ Service calls

| Service | Description |
|---------|-------------|
| `deauth_guard.get_history` | Return recent stored detection records |
| `deauth_guard.clear_history` | Clear the integration’s local history store (not Recorder) |

Schemas live in `custom_components/deauth_guard/services.yaml`.

---

## 💡 Design principles

1. **Defensive only** — awareness for networks **you are allowed to monitor**; not a replacement for enterprise WIDS/WIPS.
2. **Stable automation surface** — treat bus **`event_type`** and structured payload keys as a public contract; bump the integration version on breaking changes.
3. **Gated alerts** — history can grow without spamming the bus; filters and rules decide **`deauth_guard_attack`**.
4. **Optional heavy deps** — keep Scapy/raw capture optional so the integration still loads in simulation without extra wheels or root.

---

## 📖 Documentation

| Doc | What’s inside |
|-----|----------------|
| [User manual](docs/USER.md) | Install, wizard fields, services, events, limitations |
| [Developer manual](docs/DEVELOPER.md) | Architecture, APIs, extension points |
| [Open decisions](docs/DECISIONS.md) | Packaging, capture stack, privileges |

**Developers:** `pip install -r requirements-dev.txt` then `python -m pytest tests/ -v` (uses `tests/ha_stubs.py`; no full `homeassistant` install required).

---

## 🔗 Similar projects (non-exhaustive)

| Project | Approach |
|---------|----------|
| [TECH7Fox/deauth-detector-hass-addons](https://github.com/TECH7Fox/deauth-detector-hass-addons) | Home Assistant **add-on** (Docker), not a bare `custom_components` integration |
| [SpacehuhnTech/DeauthDetector](https://github.com/SpacehuhnTech/DeauthDetector) | ESP8266 LED detector, often MQTT → HA |
| [deauthalyzer](https://github.com/z0m31en7/deauthalyzer) & Scapy tooling | Stand-alone Linux scripts, not first-class HA entities |

---

## 🍓 Raspberry Pi 3B

The integration targets **low memory / CPU** hosts: bounded history, no busy loops in the hot path. A Pi 3B running **real** 802.11 capture still needs a suitable **adapter + driver** and tuning — see the developer manual.

---

## 📄 License

MIT — see [`LICENSE`](LICENSE). No warranty.

> [!CAUTION]
> Use only on **networks you are authorized to monitor** and in compliance with **local law**. This software does not replace professional wireless security tooling; it is for home automation, lab, and educational defensive use.
