#!/usr/bin/env bash
set -euo pipefail
# List every SKILL.md in the repo with its directory name.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
find "$REPO/skills" -name SKILL.md -not -path '*/archive/*' -print0 |
  while IFS= read -r -d '' f; do
    printf '%s\t%s\n' "$(basename "$(dirname "$f")")" "$f"
  done | sort
