# Agent & contributor guide (AI and humans)

This repository is a **Home Assistant custom integration** that detects 802.11 deauthentication (and related) activity using a dedicated WiFi interface (typically in monitor mode on Linux).

## Non-negotiables

- **Follow** [Home Assistant development documentation](https://developers.home-assistant.io/) for structure, config flows, services, and storage.
- **All user-facing and developer documentation** in `docs/` is **English** unless a file explicitly states otherwise. **Home Assistant UI strings** for the integration are under `custom_components/deauth_guard/translations/`: keep **`en.json`** and **`fr.json`** in sync when adding or changing keys.
- **Minimize diffs**: change only what the task requires; match existing style and patterns in this tree.
- **Security & ethics**: document that monitor mode and frame capture are sensitive; this project is for **defensive monitoring** on networks you are allowed to monitor.

## Where things live

| Area | Location |
|------|----------|
| Integration domain | `custom_components/deauth_guard/` |
| User manual | `docs/USER.md` |
| Developer manual | `docs/DEVELOPER.md` |
| UI translations (EN/FR) | `custom_components/deauth_guard/translations/en.json`, `.../fr.json` |
| Architectural decisions (pending product choices) | `docs/DECISIONS.md` |
| Sniffer / capture abstractions | `custom_components/deauth_guard/capture/` |
| Event history store | `custom_components/deauth_guard/history.py` |

## Event and automation contract

- Fires Home Assistant bus events for detections. Automation authors depend on **stable event `type` values** in the payload; treat them as a public API and bump version on breaking changes.
- Prefer **structured data** (MAC addresses normalized, reason codes, RSSI, **802.11 channel**, **band** using the same string labels as `const` e.g. **`2.4 GHz` / `5 GHz` / `6 GHz`**, optional **wifi_phy** short label, `emit` when the bus event is a raised alert) over free-form text in event payloads. **Not every** stored history row produces a bus event: **channel filter** and **alert rules** gate `deauth_guard_attack`.

## Optional dependencies

- **Production capture** (Scapy, raw sockets) may require extra Python packages and **elevated privileges** on the host. Keep them optional and guard imports so the integration still loads in development (simulation mode) without them.

## Raspberry Pi 3B

- Treat **ARMv7 / memory / CPU** as constraints: avoid unbounded buffers, large default history, or busy loops in the main thread; offload blocking I/O to executors.

## When editing

- Read neighboring files before adding new modules.
- For release or HACS-related changes, follow **`.cursor/skills/hass-community-validation/SKILL.md`** and keep **hassfest + HACS** green (see `.github/workflows/validate.yml`).
- Run **`python -m pytest tests/ -v`** after changes (see `docs/DEVELOPER.md` — stubs in `tests/ha_stubs.py`, no full `homeassistant` install required).
- Run linters if available (`ruff` via `pyproject.toml`).
