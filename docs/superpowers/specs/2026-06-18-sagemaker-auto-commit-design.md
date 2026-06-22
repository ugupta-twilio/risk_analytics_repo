# SageMaker Notebook Auto-Commit to Main — Design Spec

**Date:** 2026-06-18
**Status:** Approved

---

## Problem

Analysts working in SageMaker Studio create Jupyter notebooks inside their
`projects/<area>/<ticket>/<username>/sagemaker/` folder. The existing auto-sync
hook commits to a feature branch (via `.sync-branch`), requiring a PR and human
review before work reaches `main`. For notebook work in the `sagemaker/`
subfolder, this overhead is unnecessary — notebooks should land on `main`
automatically on every save.

---

## Goal

When an analyst saves a `.ipynb` file inside their `…/<username>/sagemaker/`
folder, it is automatically committed and pushed directly to `main` — no PR,
no review step. All other files continue to use the existing `.sync-branch`
feature-branch flow.

---

## Scope

**In scope:**
- Extending `sagemaker/setup.sh` (the JupyterLab post-save hook)
- Adding a routing helper `_is_sagemaker_path()`
- Updating `sagemaker/README.md` with the new behaviour and admin onboarding step

**Out of scope:**
- Changes to `path-check.yml` or `check_paths.py`
- Changes to branch protection for non-bypass users
- Auto-merging PRs or creating any new branches

---

## Folder Convention

The target pattern is:

```
projects/<area>/<ticket>/<username>/sagemaker/<notebook>.ipynb
```

Example: `projects/GM/RISK-3016/kbhat/sagemaker/analysis.ipynb`

Only `.ipynb` files are synced. Any other file type saved inside `sagemaker/`
is silently ignored by the direct-to-main path (it falls through to the
`.sync-branch` logic, which also skips it since no `.sync-branch` exists there).

---

## Architecture

### Routing logic (`_is_sagemaker_path`)

A new helper in the post-save hook block of `setup.sh`:

```python
def _is_sagemaker_path(os_path, repo_dir):
    """True if os_path is a .ipynb file inside a …/<username>/sagemaker/ subtree."""
    if not os_path.endswith(".ipynb"):
        return False
    rel = os.path.relpath(os_path, repo_dir)
    parts = Path(rel).parts
    # Must be under projects/ and have 'sagemaker' as the immediate parent dir
    # of the file, preceded by a username folder.
    # e.g. projects/GM/RISK-3016/kbhat/sagemaker/notebook.ipynb
    #       parts: ('projects','GM','RISK-3016','kbhat','sagemaker','notebook.ipynb')
    return (
        len(parts) >= 3
        and parts[0] == "projects"
        and "sagemaker" in parts[:-1]
        and parts[list(parts).index("sagemaker") - 1] != "projects"
    )
```

### Updated `_auto_sync_on_save` flow

```
file saved
    │
    ├─ not inside repo_dir → skip
    │
    ├─ _is_sagemaker_path() == True AND file is .ipynb
    │       │
    │       ├─ git pull --rebase origin main   (prevent push rejection on concurrent saves)
    │       ├─ git add <file>
    │       ├─ git diff --cached → no change? skip commit
    │       ├─ git commit -m "auto: save <filename>"
    │       └─ git push origin main
    │
    └─ else → existing .sync-branch logic (unchanged)
               │
               ├─ no .sync-branch found → skip silently
               └─ branch found → commit + push to feature branch
```

Errors in either path are caught and written to `~/.jupyter/sync-errors.log`.
They never block the save.

### Branch protection bypass

`main` has 1-review protection for PRs. Direct pushes from bypass-listed accounts
are exempt. Each analyst's GitHub account is added to the bypass list once by
a repo admin during onboarding:

```bash
gh api repos/ugupta-twilio/risk_analytics_repo/branches/main/protection/restrictions/users \
  --method POST \
  --field users[]="<github-username>"
```

The analyst's personal SSH key — already configured by `setup.sh` — is the
credential used when the hook pushes. No new keys or tokens are introduced.

---

## Files Changed

| File | Change |
|---|---|
| `sagemaker/setup.sh` | Add `_is_sagemaker_path()` helper; update `_auto_sync_on_save` routing |
| `sagemaker/README.md` | Add "Sagemaker Notebook Auto-Sync to Main" section; add admin bypass onboarding step |

---

## Constraints

- Only `.ipynb` files trigger the direct-to-main path. `.py`, `.csv`, `.txt`, and any other type are ignored.
- The `sagemaker` folder must be named exactly `sagemaker` (lowercase).
- The folder must sit directly inside the analyst's `<username>/` folder, not nested deeper.
- Bypass list addition is a **manual admin step** — the analyst cannot add themselves.
- `git pull --rebase` before commit handles concurrent saves from multiple analysts. Rebase conflicts (extremely unlikely for notebook files) are logged and the save is not blocked.

---

## Verification

1. Analyst runs `setup.sh` (or re-runs to pick up updated hook)
2. Admin runs the `gh api` bypass command for the analyst's username
3. Analyst restarts their Studio space
4. Analyst creates `projects/<area>/<ticket>/<username>/sagemaker/test.ipynb`
5. Saves with Ctrl+S
6. Checks: `git log --oneline origin/main -3` — expect top commit `auto: save test.ipynb`
7. Saves a `.py` file in the same folder — confirm no new commit on `main`
8. Saves a `.ipynb` file outside the `sagemaker/` subfolder — confirm it uses `.sync-branch` flow (or skips if no `.sync-branch`)
