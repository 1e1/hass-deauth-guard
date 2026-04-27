---
name: hass-community-validation
description: >-
  Validates Home Assistant custom integrations and HACS publishability using hassfest,
  HACS action, manifest/brand/hacs.json rules, and community inclusion checklists. Use
  when preparing a release, fixing CI validation errors, or when the user mentions HACS,
  hassfest, custom component quality, or default repository requirements.
---

# Home Assistant & HACS community validation

## Goal

Make the repository pass **hassfest** and **HACS** validation (same jobs as for [hacs/default](https://github.com/hacs/default) inclusion) and stay aligned with [integration manifest](https://developers.home-assistant.io/docs/creating_integration_manifest) and [HACS publish](https://hacs.xyz/docs/publish/integration) docs.

## Quick checks in-repo

| File / path | Rule |
|-------------|------|
| `custom_components/<domain>/manifest.json` | Required keys: `domain`, `name`, `version`, `documentation`, `issue_tracker`, `codeowners`, `config_flow` if used, `iot_class`, `integration_type`, `requirements` (array). Custom integrations need `version` (SemVer/CalVer). Add `single_config_entry` when only one instance is allowed. |
| `hacs.json` (repo root) | At least `name`. Set `homeassistant` to the **lowest** HA version the code supports. Optional: `render_readme`, `hacs` (min HACS version). |
| `custom_components/<domain>/brand/icon.png` | HACS requires brand assets; `icon.png` is mandatory before falling back to [home-assistant/brands](https://github.com/home-assistant/brands). |
| `custom_components/<domain>/services.yaml` | Must match `async_register` / `async_register` services: every action has a description; services returning data use `supports_response=SupportsResponse.ONLY` (or `OPTIONAL`) in Python and a `response:` block in YAML. |
| `README.md` | Clear install steps; for HACS default you also need a **GitHub description**, **topics**, **issues enabled**, and at least one **Release** (not just a tag). |

## Hassfest without GitHub (Docker)

From the repository root (path containing `custom_components/` and `hacs.json`):

```bash
docker pull ghcr.io/home-assistant/hassfest
docker run --rm -v "$(pwd):/github/workspace" ghcr.io/home-assistant/hassfest
```

This is the same image and mount as **`home-assistant/actions/hassfest`**. HACS validation is not this container; use the **Validate** workflow on GitHub for `hacs/action`, or see [HACS Action](https://hacs.xyz/docs/publish/action/).

## CI (source of truth)

Workflow **`.github/workflows/validate.yml`** runs:

1. `home-assistant/actions/hassfest@master` — schema, manifest, services, translations, and integration rules.
2. `hacs/action@main` with `category: integration` — HACS manifest, structure, brands, `hacs.json`.

If either fails, fix the reported file before opening a PR to [hacs/default](https://github.com/hacs/default).

## Agent workflow

1. Run the **Validate** workflow (or open a PR) and read the **first failing** step log.
2. For hassfest: address domain-specific messages (manifest, `services.yaml`, `translations`, `config_flow`).
3. For HACS: if `brands` fails, add missing `brand/icon.png` (or correct path). If `description` / `topics` / `issues` fail, these are **repository settings** on GitHub, not code — update the remote repo and re-run.
4. After green CI, for default store listing: create a **GitHub Release**, then follow [Include default repositories](https://hacs.xyz/docs/publish/include).

## Ignoring checks (last resort)

`hacs/action` accepts `ignore: "check1 check2"` (see [HACS Action](https://hacs.xyz/docs/publish/action/)). **Do not** ignore checks for default submission unless align with HACS maintainers. Prefer fixing the repo.

## Further reading

- [Brand images (developer docs)](https://developers.home-assistant.io/docs/core/integration/brand_images) — `brand/` in the integration tree.
- [HACS integration requirements](https://hacs.xyz/docs/publish/integration) — structure, `manifest`, brands.
