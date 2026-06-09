#!/usr/bin/env python3
"""
Regenerates the analyst section of .github/CODEOWNERS by scanning
projects/<area>/<ticket>/<username>/ directories.

The ticket-lead section (above the ANALYST_MARKER line) is preserved unchanged.
"""
import re
import sys
from pathlib import Path

# Ticket folders must match e.g. RISK-3016, JIRA-123 (uppercase letters, hyphen, digits)
TICKET_PATTERN = re.compile(r"^[A-Z]+-\d+$")

ANALYST_MARKER = "# ── Analyst folders ───────────────────────────────────────"
REPO_ROOT = Path(__file__).parent.parent
CODEOWNERS_PATH = REPO_ROOT / ".github" / "CODEOWNERS"


def scan_analyst_folders(projects_root: Path) -> dict:
    """
    Returns {relative_folder_path: github_username} for all
    projects/<area>/<ticket>/<username>/ directories.
    """
    result = {}
    if not projects_root.exists():
        return result
    for area in sorted(projects_root.iterdir()):
        if not area.is_dir() or area.name.startswith("_"):
            continue
        for ticket in sorted(area.iterdir()):
            if not ticket.is_dir() or not TICKET_PATTERN.match(ticket.name):
                continue
            for username_dir in sorted(ticket.iterdir()):
                if not username_dir.is_dir():
                    continue
                rel = username_dir.relative_to(REPO_ROOT)
                result[str(rel) + "/"] = username_dir.name
    return result


def build_analyst_section(folders: dict) -> str:
    lines = [ANALYST_MARKER]
    lines.append("# Each analyst must approve PRs touching their own folder")
    if not folders:
        lines.append("# (no analyst folders found)")
    else:
        max_len = max(len(f) for f in folders)
        for folder, username in sorted(folders.items()):
            lines.append(f"{folder:<{max_len}}  @{username}")
    return "\n".join(lines) + "\n"


def update_codeowners() -> bool:
    """Returns True if CODEOWNERS was changed."""
    existing = CODEOWNERS_PATH.read_text() if CODEOWNERS_PATH.exists() else ""

    # Split at the analyst marker; keep the lead section
    if ANALYST_MARKER in existing:
        lead_section = existing[: existing.index(ANALYST_MARKER)].rstrip() + "\n\n"
    else:
        lead_section = existing.rstrip() + "\n\n"

    folders = scan_analyst_folders(REPO_ROOT / "projects")
    analyst_section = build_analyst_section(folders)
    new_content = lead_section + analyst_section

    if new_content == existing:
        print("CODEOWNERS is already up to date.")
        return False

    CODEOWNERS_PATH.write_text(new_content)
    print(f"CODEOWNERS updated with {len(folders)} analyst folder(s).")
    return True


if __name__ == "__main__":
    update_codeowners()
    sys.exit(0)  # always exit 0; caller checks git diff
