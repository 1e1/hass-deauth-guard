# Open product and architecture decisions

This document records decisions that **require your input**. Until each row is **Resolved**, the implementation may use a **provisional** default (clearly marked in code or in `DEVELOPER.md`).

| ID | Topic | Status |
|----|--------|--------|
| D1 | Delivery model: custom integration only vs add-on / companion daemon | **Open** |
| D2 | Frame capture stack: Scapy vs `tcpdump`/`tshark` vs `libpcap` bindings | **Open** |
| D3 | Privilege model: host capabilities vs container vs dedicated sidecar | **Open** |
| D4 | History: fixed ring buffer only vs opt-in `recorder` / long-term DB | **Open** |

## Channel policy (UI / product)

**Resolved in code (0.2.x):**

- **Q: Is it easier to scan only restricted channels?** **Partly yes** for real radios (less spectrum to visit); for pure software filtering, the win is **less noise in HA**, not less RF work unless the sniffer is also channel-limited.
- **Implementation:** If the user selects one or more channels, **known** frame channel **not in** the set → **drop** (debug log). **Unknown** channel → **keep** (do not hide unknown metadata). **Simulation** does **not** apply the allow-list; synthetic events use **random** channels on a **10s** default cadence.
- **Alternative (not implemented):** “Log-only” for off-list channels would duplicate paths; the project chose **drop** when restricted, per product ask.

## D1 — Delivery model

| Option | Pros | Cons |
|--------|------|------|
| **A. Custom integration only** (this repo) | Simple install via HACS; single codebase; easy dev inner loop with simulation | Raw WiFi / monitor mode often needs **root or capabilities** that HA Core on minimal Linux may not grant; harder on HA OS without extra privileges |
| **B. Add-on (Docker) + optional integration** | Isolated privilege boundary; can `network_mode: host` and `privileged` in one place | Two artifacts to maintain; Supervised/HA OS–centric |
| **C. Companion process** (systemd) + small HA integration (MQTT/REST) | Clean separation: root for sniffer, least privilege for HA | More moving parts; you operate two services |

**Provisional default in repo:** **A** with a **simulation** capture for development; production path documented in `DEVELOPER.md` once D2–D3 are set.

## D2 — Frame capture stack

| Option | Pros | Cons |
|--------|------|------|
| **A. Scapy** | Python-native; flexible parsing; well-known in security tooling | Heavier; careful with performance on RPi3B; optional native deps can be finicky on ARM |
| **B. `tcpdump` + parse** (subprocess) | Mature, fast path; can match OS packages | Subprocess/parse overhead; you own wire format / upgrades |
| **C. `tshark` (pyshark) / pcap to JSON** | Rich dissection (including 802.11) | Heavier; still subprocess unless linked as lib; resource use on RPi3B needs tuning |

**Provisional default:** start with a **pluggable** `DeauthEventSource` in code; first concrete impl can be **simulation**, then **A or B** based on D3.

## D3 — Privilege model

| Option | Pros | Cons |
|--------|------|------|
| **A. `CAP_NET_RAW` / `CAP_NET_ADMIN` on HA process** | No extra process | May be too wide; not always sufficient for all drivers |
| **B. Setuid helper / small C helper** | Least code in Python; clearly bounded | Another binary to ship and audit |
| **C. Add-on or systemd unit as root, HA integration as client** | HA stays unprivileged; sniffer is explicit | See D1 complexity |

**Provisional default:** document **B or C** for real monitor mode; do not silently assume root inside Core.

## D4 — Event history

| Option | Pros | Cons |
|--------|------|------|
| **A. In-Home Assistant `Store` (JSON), bounded ring** | No DB dependency; matches current scaffold | Not ideal for very large history; backup size |
| **B. `recorder` + events only** | Native HA; automations and UI patterns | You depend on user retention and exclude/include filters |
| **C. Local SQLite in integration** | Long history, queryable | New maintenance surface; migrations |

**Provisional default:** **A** (bounded) + optional **B** documented for users who want long history in the standard recorder.

---

**Maintainer:** when you choose options, update this file with `Status: Resolved` and a one-line rationale, then adjust `DEVELOPER.md` and the integration defaults accordingly.
