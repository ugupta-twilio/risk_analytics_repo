import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CheckResult:
    allowed: bool
    blocked_files: list = field(default_factory=list)
    error_message: str = ""
    is_provisioning: bool = False


def _analyst_folder_for(path: str, actor: str) -> bool:
    """True if path is inside projects/**/<actor>/"""
    parts = Path(path).parts
    return len(parts) >= 4 and parts[0] == "projects" and parts[3] == actor


def _ticket_prefix(path: str) -> Optional[str]:
    """Return 'projects/<area>/<ticket>' for a path, or None."""
    parts = Path(path).parts
    if len(parts) >= 3 and parts[0] == "projects":
        return str(Path(*parts[:3]))
    return None


def _new_folder_owner(changed: list) -> Optional[str]:
    """If all changed files are under a single new username folder, return that username."""
    owners = set()
    for f in changed:
        parts = Path(f).parts
        if len(parts) >= 4 and parts[0] == "projects":
            owners.add(parts[3])
    return owners.pop() if len(owners) == 1 else None


PROVISIONING_ALLOWED_FILES = {"README.md", "__init__.py"}


def is_provisioning_pr(changed: list) -> bool:
    """True if PR only adds a single new username folder with README.md and __init__.py."""
    owner = _new_folder_owner(changed)
    if not owner:
        return False
    filenames = {Path(f).name for f in changed}
    return filenames <= PROVISIONING_ALLOWED_FILES


def classify_files(
    changed: list,
    actor: str,
    leads: dict,
    admins: list = None,
    is_new_folder_only: bool = False,
) -> CheckResult:
    admins = admins or []

    if is_new_folder_only:
        owner = _new_folder_owner(changed)
        if owner == actor:
            return CheckResult(allowed=True, is_provisioning=True)
        return CheckResult(
            allowed=False,
            blocked_files=changed,
            error_message=(
                f"Self-provisioning PR: folder name '{owner}' does not match "
                f"your GitHub username '{actor}'."
            ),
        )

    blocked = []
    for f in changed:
        if _analyst_folder_for(f, actor):
            continue
        if f.startswith(".github/"):
            if actor in admins:
                continue
            blocked.append(f)
            continue
        prefix = _ticket_prefix(f)
        if prefix:
            if prefix not in leads:
                return CheckResult(
                    allowed=False,
                    blocked_files=[f],
                    error_message=(
                        f"No lead configured for '{prefix}'. Contact repo admin."
                    ),
                )
            if leads[prefix] == actor:
                continue
        blocked.append(f)

    if blocked:
        return CheckResult(
            allowed=False,
            blocked_files=blocked,
            error_message=(
                f"The following files are outside your allowed folders:\n"
                + "\n".join(f"  {b}" for b in blocked)
                + f"\nOnly touch projects/**/{actor}/ or ticket-level files if you are the lead."
            ),
        )
    return CheckResult(allowed=True)


def main():
    changed_files = os.environ.get("CHANGED_FILES", "").splitlines()
    actor = os.environ.get("GITHUB_ACTOR", "")
    admins_raw = os.environ.get("REPO_ADMINS", "")
    admins = [a.strip() for a in admins_raw.split(",") if a.strip()]

    leads_path = Path("../leads.json")
    if not leads_path.exists():
        print("ERROR: leads.json not found.")
        sys.exit(1)
    leads = json.loads(leads_path.read_text())

    if not changed_files or not actor:
        print("ERROR: CHANGED_FILES and GITHUB_ACTOR must be set.")
        sys.exit(1)

    result = classify_files(
        changed=changed_files,
        actor=actor,
        leads=leads,
        admins=admins,
        is_new_folder_only=is_provisioning_pr(changed_files),
    )

    if result.is_provisioning:
        print(f"✅ Self-provisioning PR detected for '{actor}'. Ticket lead review required.")
        sys.exit(0)

    if result.allowed:
        print(f"✅ All changed files are within allowed paths for '{actor}'.")
        sys.exit(0)

    print(f"❌ Path check failed:\n{result.error_message}")
    sys.exit(1)


if __name__ == "__main__":
    main()
