#!/usr/bin/env python3
"""Build the uploadable skill archive.

Produces `dist/jira-card.zip` with the skill folder (`jira-card/`) at the ZIP
root and a Claude.ai-compatible description (<= 200 chars, taken verbatim from
`scripts/skill-dist-description.txt`). The repo's own SKILL.md keeps its long,
trigger-rich description for Claude Code; only the packaged copy is shortened.

Run locally or in CI:  python3 scripts/build_skill_zip.py
Override the repo root with SKILL_REPO_ROOT (used by tests).
"""
from __future__ import annotations
import os
import pathlib
import sys
import zipfile

ROOT = pathlib.Path(os.environ.get(
    "SKILL_REPO_ROOT", pathlib.Path(__file__).resolve().parent.parent))
SKILL_DIR = ROOT / "skills" / "jira-card"
DESC_FILE = ROOT / "scripts" / "skill-dist-description.txt"
OUT = ROOT / "dist" / "jira-card.zip"
MAX_DESC = 200  # Claude.ai upload limit


def shortened_skill_md() -> str:
    desc = DESC_FILE.read_text(encoding="utf-8").strip()
    if len(desc) > MAX_DESC:
        sys.exit(f"ERROR: dist description is {len(desc)} chars (> {MAX_DESC})")
    out = []
    replaced = False
    for line in (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("description:") and not replaced:
            out.append("description: " + desc)
            replaced = True
        else:
            out.append(line)
    if not replaced:
        sys.exit("ERROR: no `description:` line found in SKILL.md")
    return "\n".join(out) + "\n"


def main() -> None:
    if not SKILL_DIR.is_dir():
        sys.exit(f"ERROR: skill dir not found: {SKILL_DIR}")
    skill_md = shortened_skill_md()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(SKILL_DIR.rglob("*")):
            if path.is_dir() or path.name.startswith("."):
                continue
            arc = "jira-card/" + str(path.relative_to(SKILL_DIR))
            if path == SKILL_DIR / "SKILL.md":
                z.writestr(arc, skill_md)
            else:
                z.write(path, arc)
    desc_len = len(DESC_FILE.read_text(encoding="utf-8").strip())
    print(f"built {OUT.relative_to(ROOT)} "
          f"({OUT.stat().st_size} bytes, description {desc_len} chars)")


if __name__ == "__main__":
    main()
