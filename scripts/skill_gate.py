#!/usr/bin/env python3
"""Prompt-safety gate for the jira-card skill (enterprise CI gate).

Fails (exit 1) if the skill's prompts / shipped content:
  1. break structure or metadata rules,
  2. drop a safety guardrail (regression),
  3. contain dangerous or prompt-injection instructions,
  4. leak organisation / internal-project identifiers, or
  5. embed secrets or real Jira instance IDs.

Deterministic, offline, no third-party deps — runs identically in CI and locally.
Scope: the shipped skill + project docs. The CI tooling under scripts/ and
.github/ is excluded (it legitimately contains the detection patterns themselves);
whole-repo secret scanning is handled separately by gitleaks in CI.

Override the repo root with SKILL_REPO_ROOT (used by the self-test).
"""
from __future__ import annotations
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(os.environ.get(
    "SKILL_REPO_ROOT", pathlib.Path(__file__).resolve().parent.parent))
SKILL_DIR = ROOT / "skills" / "jira-card"

GREEN, RED, RESET = "\033[32m", "\033[31m", "\033[0m"
failures: list[str] = []


def fail(check: str, msg: str) -> None:
    failures.append(f"{check}: {msg}")


def ok(check: str, msg: str) -> None:
    print(f"  {GREEN}PASS{RESET} {check} — {msg}")


def read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


if not SKILL_DIR.is_dir():
    sys.exit(f"FATAL: skill directory not found: {SKILL_DIR}")

skill_md_path = SKILL_DIR / "SKILL.md"
prompt_files = sorted(p for p in SKILL_DIR.rglob("*.md") if p.is_file())

# Shipped/representative content scanned for leaks (NOT the CI tooling, which
# contains the patterns below). Whole-repo secrets are covered by gitleaks.
content_files = list(prompt_files)
for rel in ("skills/jira-card/config.example.json", "README.md",
            "CONTRIBUTING.md", "CLAUDE.md", ".claude-plugin/plugin.json"):
    p = ROOT / rel
    if p.is_file():
        content_files.append(p)

# ----------------------------------------------------------- 1. structure
if not skill_md_path.exists():
    fail("structure", "SKILL.md missing")
else:
    md = read(skill_md_path)
    fm = re.search(r"\A---\n(.*?)\n---", md, re.S)
    if not fm:
        fail("structure", "missing YAML frontmatter")
    else:
        name = re.search(r"^name:\s*(.+?)\s*$", fm.group(1), re.M)
        desc = re.search(r"^description:\s*(.+?)\s*$", fm.group(1), re.M)
        if not name:
            fail("structure", "no `name` field")
        elif not re.fullmatch(r"[a-z0-9-]{1,64}", name.group(1)):
            fail("structure", f"name '{name.group(1)}' must match [a-z0-9-]{{1,64}}")
        elif name.group(1) != SKILL_DIR.name:
            fail("structure", f"name '{name.group(1)}' != folder '{SKILL_DIR.name}'")
        else:
            ok("structure", f"name '{name.group(1)}' valid & matches folder")
        if not desc:
            fail("structure", "no `description` field")
        elif len(desc.group(1)) > 1024:
            fail("structure", f"description {len(desc.group(1))} chars > 1024 (spec max)")
        else:
            ok("structure", f"description {len(desc.group(1))} chars (<= 1024)")
    for ref in sorted(set(re.findall(r"reference/([a-z0-9-]+\.md)", md))):
        if (SKILL_DIR / "reference" / ref).exists():
            ok("structure", f"reference/{ref} present")
        else:
            fail("structure", f"SKILL.md references reference/{ref} but it is missing")

cfg = SKILL_DIR / "config.example.json"
if cfg.exists():
    try:
        json.loads(read(cfg))
        ok("structure", "config.example.json is valid JSON")
    except Exception as e:
        fail("structure", f"config.example.json invalid JSON: {e}")

# ----------------------------------------------------------- 2. guardrail invariants
GUARDRAILS = {
    "one-confirmation-before-write": r"[Oo]ne confirmation before writing",
    "done-needs-explicit-approval": r"explicit approval",
    "never-auto-commit": r"never[ -]auto-?committ?ed?|never auto-commit",
}
gtxt = read(skill_md_path) if skill_md_path.exists() else ""
for key, pat in GUARDRAILS.items():
    if re.search(pat, gtxt):
        ok("guardrail", key)
    else:
        fail("guardrail", f"safety invariant removed from SKILL.md: {key}")

# ----------------------------------------------------------- 3. dangerous instructions
DANGER = {
    "destructive-shell": r"rm\s+-rf\s+[/$~]|--no-preserve-root|\bmkfs\b|\bdd\s+if=",
    "pipe-to-shell": r"(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z)?sh\b",
    "bypass-safety": r"\b(bypass|disable|circumvent|override)\b[^\n]{0,20}\b(confirmation|approval|guardrail|safety|gate)\b",
    "prompt-injection": r"ignore\s+(all\s+)?previous\s+instructions|disregard\s+(the\s+)?(system|above|previous)|you\s+are\s+now\s+(a|an|DAN)\b",
    "exfiltration": r"\b(POST|send|upload|exfiltrat\w*)\b[^\n]{0,40}\b(secret|token|credential|password|api[_-]?key|\.ssh|\.env)\b",
}
for p in prompt_files:
    txt = read(p)
    rel = p.relative_to(ROOT)
    for key, pat in DANGER.items():
        for m in re.finditer(pat, txt, re.I):
            fail("danger", f"{rel}: {key} -> '{m.group()[:60].strip()}'")
if not any(f.startswith("danger") for f in failures):
    ok("danger", "no dangerous or prompt-injection instructions in prompts")

# ----------------------------------------------------------- 4. org / internal-project leak
ORG = [
    (r"bdithailand", re.I), (r"\bbdi\b", re.I), (r"\bnbdp\b", re.I),
    (r"\bgbdi\b", re.I), (r"\bdii\b", re.I), (r"data\.go\.th", re.I),
    (r"data_go_th", re.I), (r"\bsql[-_ ]?agents?\b", re.I),
    (r"aws-athena-mcp", re.I), (r"\bathena\b", re.I),
    (r"\bDIT\b", 0), (r"\bD2\b", 0),
]
org_hits = 0
for p in content_files:
    txt = read(p)
    rel = p.relative_to(ROOT)
    for pat, flags in ORG:
        for m in re.finditer(pat, txt, flags):
            fail("org-leak", f"{rel}: '{m.group()}'")
            org_hits += 1
if org_hits == 0:
    ok("org-leak", "no organisation / internal-project identifiers in shipped content")

# ----------------------------------------------------------- 5. secrets / real instance IDs
SECRETS = {
    "aws-access-key": r"AKIA[0-9A-Z]{16}",
    "private-key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "atlassian-token": r"ATATT[0-9A-Za-z_\-]{20,}",
    "generic-secret": r"(?i)\b(api[_-]?key|secret|password|access[_-]?token|auth[_-]?token)\b\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{20,}",
    "real-uuid": r"\b(?!0{8}-0{4}-0{4}-0{4}-0{12}\b)[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
    "email": r"\b[A-Za-z0-9._%+\-]+@(?!example\.|your-org\.)[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
}
sec_hits = 0
for p in content_files:
    txt = read(p)
    rel = p.relative_to(ROOT)
    for key, pat in SECRETS.items():
        for m in re.finditer(pat, txt):
            fail("secret", f"{rel}: {key} -> '{m.group()[:40]}'")
            sec_hits += 1
if sec_hits == 0:
    ok("secret", "no secrets or real instance IDs in shipped content")

# ----------------------------------------------------------- verdict
print()
if failures:
    print(f"{RED}GATE FAILED — {len(failures)} issue(s):{RESET}")
    for f in failures:
        print(f"  {RED}x{RESET} {f}")
    sys.exit(1)
print(f"{GREEN}GATE PASSED — skill prompts and content are safe to ship.{RESET}")
