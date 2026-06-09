import pytest
from check_paths import classify_files, CheckResult, is_provisioning_pr

LEADS = {"projects/GM/RISK-3016": "ugupta-twilio"}

# ── classify_files ─────────────────────────────────────────────────────────

def test_own_folder_allowed():
    result = classify_files(
        changed=["projects/GM/RISK-3016/kbhat27s/notebook.ipynb"],
        actor="kbhat27s",
        leads=LEADS,
    )
    assert result.allowed is True
    assert result.blocked_files == []

def test_own_folder_allowed_2level():
    # projects/<username>/file — e.g. projects/skuanar/ReadMe.md
    result = classify_files(
        changed=["projects/skuanar/ReadMe.md"],
        actor="skuanar",
        leads=LEADS,
    )
    assert result.allowed is True

def test_own_folder_allowed_3level():
    # projects/<area>/<username>/file — e.g. projects/test/ugupta-twilio/test.py
    result = classify_files(
        changed=["projects/test/ugupta-twilio/test.py"],
        actor="ugupta-twilio",
        leads=LEADS,
    )
    assert result.allowed is True

def test_other_analyst_folder_blocked():
    result = classify_files(
        changed=["projects/GM/RISK-3016/klalwani01/notebook.ipynb"],
        actor="kbhat27s",
        leads=LEADS,
    )
    assert result.allowed is False
    assert "projects/GM/RISK-3016/klalwani01/notebook.ipynb" in result.blocked_files

def test_ticket_root_allowed_for_lead():
    result = classify_files(
        changed=["projects/GM/RISK-3016/README.md"],
        actor="ugupta-twilio",
        leads=LEADS,
    )
    assert result.allowed is True

def test_ticket_root_blocked_for_non_lead():
    result = classify_files(
        changed=["projects/GM/RISK-3016/README.md"],
        actor="kbhat27s",
        leads=LEADS,
    )
    assert result.allowed is False

def test_github_dir_blocked_for_non_admin():
    result = classify_files(
        changed=[".github/leads.json"],
        actor="kbhat27s",
        leads=LEADS,
        admins=["ugupta-twilio"],
    )
    assert result.allowed is False

def test_github_dir_allowed_for_admin():
    result = classify_files(
        changed=[".github/leads.json"],
        actor="ugupta-twilio",
        leads=LEADS,
        admins=["ugupta-twilio"],
    )
    assert result.allowed is True

def test_ticket_root_blocked_when_no_lead_configured():
    # No lead in leads.json — ticket-level file is blocked as unauthorized, no special error
    result = classify_files(
        changed=["projects/GM/RISK-9999/README.md"],
        actor="kbhat27s",
        leads={},
    )
    assert result.allowed is False
    assert "projects/GM/RISK-9999/README.md" in result.blocked_files
    assert "No lead configured" not in result.error_message

def test_self_provisioning_pr_allowed():
    result = classify_files(
        changed=[
            "projects/GM/RISK-3016/newuser/README.md",
            "projects/GM/RISK-3016/newuser/__init__.py",
        ],
        actor="newuser",
        leads=LEADS,
        is_new_folder_only=True,
    )
    assert result.allowed is True
    assert result.is_provisioning is True

def test_self_provisioning_wrong_username_blocked():
    result = classify_files(
        changed=[
            "projects/GM/RISK-3016/otheruser/README.md",
            "projects/GM/RISK-3016/otheruser/__init__.py",
        ],
        actor="newuser",
        leads=LEADS,
        is_new_folder_only=True,
    )
    assert result.allowed is False

# ── is_provisioning_pr ─────────────────────────────────────────────────────

def test_detects_provisioning_pr():
    assert is_provisioning_pr(
        ["projects/GM/RISK-3016/newuser/README.md",
         "projects/GM/RISK-3016/newuser/__init__.py"]
    ) is True

def test_not_provisioning_when_extra_files():
    assert is_provisioning_pr(
        ["projects/GM/RISK-3016/newuser/README.md",
         "projects/GM/RISK-3016/newuser/notebook.ipynb"]
    ) is False

def test_not_provisioning_when_multiple_folders():
    assert is_provisioning_pr(
        ["projects/GM/RISK-3016/newuser/README.md",
         "projects/GM/RISK-3016/otheruser/README.md"]
    ) is False

def test_provisioning_with_sync_branch_file():
    # .sync-branch is now a required file in analyst folders — provisioning PR should include it
    assert is_provisioning_pr(
        ["projects/GM/RISK-3016/newuser/README.md",
         "projects/GM/RISK-3016/newuser/__init__.py",
         "projects/GM/RISK-3016/newuser/.sync-branch"]
    ) is True
