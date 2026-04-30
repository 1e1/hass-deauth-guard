# User manual — Deauth Guard (`deauth_guard`)

## What it does

**Deauth Guard** helps you **notice patterns consistent with 802.11 deauthentication** activity observed on a WiFi radio you control, so you can build **automations** (notifications, countermeasures, logging) in Home Assistant.

**What it is not:** It does not replace a professional **wireless IDS/IPS** or a managed enterprise AP platform. It does not stop attacks by itself. Use it for **awareness and home automation** on **networks you are authorized to monitor**.

## Legal and ethical use

Only use this software in compliance with **local law** and **network policy**. Capturing or injecting wireless traffic without authorization is illegal in many jurisdictions. The authors provide software **for defensive and educational use** on your own systems.

## Requirements

- **Home Assistant** 2024.1 or newer (aligned with `hacs.json`).
- A **Linux-based host** (including Raspberry Pi OS) where a WiFi interface can be placed in **monitor mode** (when you select a real interface and a capture backend exists).
- Often **root-equivalent capabilities** for raw 802.11 access. See the Developer manual and `docs/DECISIONS.md`.

**Raspberry Pi 3B:** supported as a *lightweight* platform; for heavy capture, consider a faster board or a dedicated external adapter.

## Installation

### Via HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=agerlier&repository=ha-deauth&category=integration)

1. Click the button above **or** open HACS → Integrations → ⋮ → **Custom repositories**
2. Add `https://github.com/agerlier/ha-deauth` as **Integration**
3. Install **Deauth Guard**
4. **Restart** Home Assistant

### Manual (custom component)

1. Copy the folder `deauth_guard` from this repository’s `custom_components` directory into your Home Assistant configuration directory, under `custom_components/`, so you have:

   `config/custom_components/deauth_guard/...`

2. **Restart** Home Assistant

### After install (both paths)

3. **Settings → Devices & services → Add integration** and search for **Deauth Guard**.

4. Complete the **configuration wizard** (see below). You can change options later under **Configure** on the integration card.

## Setup wizard and reconfiguration

The integration uses a **single** Home Assistant config entry. You can run **simulation**, **one** physical interface (when capture exists), or **up to three** Wi‑Fi sources (Radio 1 required; Radio 2 and 3 optional). **Alert rules**, **history size**, and **simulation interval** are **shared** across all radios.

| Field | Description |
|--------|-------------|
| **Radio 1 — interface** | **Simulation (no radio)** for tests without hardware, or a **real** interface from the host (Linux list). Real capture is not implemented yet; a physical choice prepares the config for a future release. |
| **Radio 1 — channels** | **Multi-select** for that radio only. **Empty** = no software filter on that interface (all reported channels). If you select channels, events on other channels are **dropped** for history and alerts when the event is tied to that interface. |
| **Radio 2 / Radio 3** | Optional extra interfaces. Use **“—”** to disable a slot. Duplicates are ignored. If Radio 1 is **Simulation**, extra radios are not used. |
| **Seconds between simulated events** | Only relevant in **simulation**. Default **10** s. Synthetic events use **random** channels (not limited to your selection) to exercise automations. |
| **Maximum history entries** | Local store size (ring buffer), shared. |
| **Alert rules (two optional rows)** | **Common** to all radios. Each row: **minimum deauth count** and **sliding window (seconds)**. If both values in a row are **0**, that row is disabled. If **no** row is active: on a **real** interface, only the **first** post-filter detection after reload raises **`deauth_guard_attack`**; in **simulation** with no rules, **every** tick can raise an event. Active rules use a **sliding window**; when the count in the window reaches the minimum, an event is emitted and that rule’s window is reset. |

## Configuration storage (JSON reference)

There is **no** `deauth_guard:` block in `configuration.yaml` for normal setup. Options live in the integration’s **config entry** under the top-level key **`options`** (alongside **`data`**, **`title`**, **`version`**, with **`domain`**: `deauth_guard`). To inspect on disk, open **`.storage/core.config_entries`** in your config folder (search for `"deauth_guard"`) or restore from a **full configuration backup**. The JSON below documents that **`options`** object—useful for **migrations**, **comparing instances**, or **debugging**.

Wi‑Fi sources and per-radio channel lists live only under **`radios`**.

### Simulation (no hardware)

```json
{
  "radios": [
    {
      "interface": "simulation",
      "channels": []
    }
  ],
  "simulation_mode": true,
  "simulation_interval_seconds": 10,
  "history_max_entries": 100,
  "alert_rules": []
}
```

With two alert rules (example: at least 5 deauths in 60 s, or 10 in 300 s):

```json
{
  "alert_rules": [
    { "min_count": 5, "window_seconds": 60 },
    { "min_count": 10, "window_seconds": 300 }
  ]
}
```

(Other keys omitted; merge with the first example.)

### Single hardware (one interface)

When Radio 1 is a real interface, **Radio 1 channels** apply only to events tagged with that `interface` name. Empty `channels` means no software filter on that radio.

```json
{
  "radios": [
    {
      "interface": "wlan0",
      "channels": [1, 6, 11]
    }
  ],
  "simulation_mode": false,
  "simulation_interval_seconds": 10,
  "history_max_entries": 100,
  "alert_rules": []
}
```

### Multi-hardware (up to three radios)

Each element of **`radios`** is one Wi‑Fi source: its own **`interface`** and **`channels`** list. **Alert rules** and **history** remain at the top level (shared).

```json
{
  "radios": [
    { "interface": "wlan0", "channels": [1, 6, 11] },
    { "interface": "wlan1", "channels": [36, 40, 44, 48, 52] }
  ],
  "simulation_mode": false,
  "simulation_interval_seconds": 10,
  "history_max_entries": 200,
  "alert_rules": [
    { "min_count": 3, "window_seconds": 120 }
  ]
}
```

A third radio would add another object to **`radios`**. The UI only exposes three slots; the stored list is the source of truth.

### Is restricted channel selection “easier”?

**Physically** (hop/monitor on fewer channels), **yes** — less spectrum to cover, often better for small boards. **In software** (filtering after capture), it only reduces **noise in Home Assistant**, not airtime, unless the capture path also limits tuning. This project’s **empty selection = all**; **non-empty** = stricter **software** filter. If we did not restrict channels, we would log more off-channel context; the current product choice is: **when you restrict, we drop** (and debug-log), not a separate “info only” path.

## Services

(Defined in `custom_components/deauth_guard/services.yaml`.)

- **`deauth_guard.get_history`** — Returns recent **stored** rows (all that passed the channel filter), not only rows that raised an event.
- **`deauth_guard.clear_history`** — Clears the integration store (not the `recorder`).

## Events (automations)

Subscribe to **`deauth_guard_attack`**. This fires when the **alert policy** says so, not on every stored row.

```yaml
trigger:
  - platform: event
    event_type: deauth_guard_attack
```

Inspect `data` in **Developer tools → Events** (MACs, `channel`, `band` (e.g. `2.4 GHz` in simulation), `wifi_phy`, `simulation`, `emit`, etc.).

## Entities

**Last deauth event** sensor reflects the most recent **stored** row after the channel filter (not only bus events).

## Troubleshooting

- **No `deauth_guard_attack` after the first (real mode, no rules):** By design, only the **first** alert per reload. Add an alert rule or use **simulation** to test repeated events.
- **Simulation not matching selected channels:** Expected — simulation uses **random** channels on each tick to exercise the stack.
- **No events in production (non-simulation):** Capture backend not implemented yet; see `docs/DECISIONS.md`.

## User interface language

The integration ships **English** and **French** config flow, service, and entity strings (`translations/en.json` and `translations/fr.json`). Home Assistant uses your **user profile language**; add other locales by copying `en.json` to a new language code (e.g. `de.json`) and translating.

## Further reading

- [Developer manual](DEVELOPER.md)
- [Open decisions](DECISIONS.md)
