#!/usr/bin/env sh
# Reminder: full validation runs in GitHub Actions (.github/workflows/validate.yml).
#
# Hassfest on any machine with Docker (from repo root — same as home-assistant/actions/hassfest):
#   docker pull ghcr.io/home-assistant/hassfest
#   docker run --rm -v "$(pwd):/github/workspace" ghcr.io/home-assistant/hassfest
# HACS is only run in CI (hacs/action) unless you replicate that environment yourself.
set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Repository: $REPO_ROOT"
echo "Required paths:"
for p in hacs.json custom_components/deauth_guard/manifest.json custom_components/deauth_guard/brand/icon.png; do
  if [ -f "$REPO_ROOT/$p" ]; then
    echo "  OK  $p"
  else
    echo "  MISSING  $p"
    exit 1
  fi
done
echo "Static layout check passed. Run CI (Validate workflow) for hassfest + HACS."
