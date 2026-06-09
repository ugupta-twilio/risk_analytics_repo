# Risk Analytics GitHub Repository + SageMaker Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a `risk-analytics` GitHub repository in the `twilio` org with per-project folder structure, branch protection, GitHub Team permissions, and SageMaker Studio auto-sync so that every notebook save in Studio automatically commits and pushes to GitHub — no manual git commands required.

**Architecture:** Each analyst runs a one-time setup script in their SageMaker Studio terminal. It generates an SSH key (stored on EFS, persists across sessions), creates a personal auto-sync branch (`auto/<username>`), clones the repo, and installs a JupyterLab post-save hook into `~/.jupyter/jupyter_server_config.py`. From that point forward, every notebook save triggers a `git add → git commit → git push` to the analyst's personal branch automatically. The `main` branch remains protected and requires a PR to merge.

**Tech Stack:** GitHub (`gh` CLI), SageMaker Studio (JupyterLab 3), SSH key auth, `bash` setup script, Python JupyterLab post-save hook.

**Actual repo used:** `ugupta-twilio/risk_analytics_repo` (public)

---

## File Map

| File | Purpose |
|---|---|
| `README.md` | Repo overview, contribution guide, contacts |
| `.gitignore` | Ignore checkpoints, `.env`, data files, credentials |
| `.github/CODEOWNERS` | RA leads auto-assigned as PR reviewers |
| `.github/pull_request_template.md` | PR checklist |
| `projects/_template/README.md` | Starter README new projects copy |
| `projects/_template/.gitkeep` | Keep the folder tracked |
| `shared/utils/.gitkeep` | Keep the folder tracked |
| `sagemaker/README.md` | SageMaker Studio auto-sync setup guide |
| `sagemaker/setup.sh` | One-time script: SSH key + repo clone + JupyterLab post-save hook install |

---

## Task 1: Pre-flight — Confirm Naming and Standards

**Files:** None created yet — this is a verification step.

- [ ] **Step 1: Confirm repo naming convention**

  Ask the Twilio DevEx / Platform team (or check internal docs) whether `risk-analytics` is acceptable:
  - Is a prefix required? (e.g., `ra-`, `data-`)
  - Is kebab-case the standard?
  - Any reserved names to avoid?

  If the name must change, substitute it throughout this plan before proceeding.

- [ ] **Step 2: Confirm internal repo visibility**

  Verify that "Internal" visibility (visible to all org members, not public) is available and the correct tier for this repo's data classification.

- [ ] **Step 3: Verify you have org-level repo creation permission**

  ```bash
  gh auth status
  gh api /orgs/twilio --jq '.login'
  ```

  Expected: your authenticated user is shown and `twilio` is returned. If you lack org creation rights, request them from the GitHub org admin before proceeding.

---

## Task 2: Create the GitHub Repository

**Files:** Creates the repo on GitHub (no local files yet).

- [x] **Step 1: Create the repo**

  Repo `ugupta-twilio/risk_analytics_repo` already existed and was used.

- [x] **Step 2: Initialize git locally and push scaffold**

  ```bash
  cd /path/to/risk-analytics
  git init
  git add .
  git commit -m "chore: initial repo scaffold with project structure and SageMaker auto-sync"
  git branch -M main
  git remote add origin https://github.com/ugupta-twilio/risk_analytics_repo.git
  git push -u origin main --force
  ```

- [x] **Step 3: Verify**

  ```bash
  gh repo view ugupta-twilio/risk_analytics_repo --json name,visibility,description
  ```

---

## Task 3: Scaffold Repository Files

**Files:** All files listed in the File Map above.

- [x] **Step 1: Create directory structure**

  ```bash
  mkdir -p .github projects/_template shared/utils sagemaker
  ```

- [x] **Step 2: Create `.gitignore`**

  Ignores: `.ipynb_checkpoints/`, `.env`, `*.pem`, `*.key`, `*.csv`, `*.parquet`, `*.json.gz`, `data/`, `__pycache__/`, `*.py[cod]`, `.DS_Store`, `.sagemaker-code-config`

- [x] **Step 3: Create `README.md`**

  Sections: Adding a New Project, SageMaker Studio Setup, Shared Utilities, Team table, Contributing rules.

- [x] **Step 4: Create `.github/CODEOWNERS`**

  ```
  # RA leads are auto-assigned as reviewers on all PRs
  * @ugupta-twilio
  ```

- [x] **Step 5: Create `.github/pull_request_template.md`**

  Checklist: no credentials, no data files, README updated, code runs end-to-end.

- [x] **Step 6: Create project template files**

  `projects/_template/README.md` with: project name, what it does, how to run, owner, last updated.
  Plus empty `.gitkeep` files in `projects/_template/` and `shared/utils/`.

- [x] **Step 7: Commit and push scaffolding**

  ```bash
  git add .
  git commit -m "chore: initial repo scaffold with project structure and PR template"
  git push -u origin main
  ```

---

## Task 4: Configure GitHub Team and Permissions

**Files:** GitHub settings (no repo files changed).

- [x] **Step 1: Identify the RA team**

  Used existing team `team_ct-risk-analytics` from the `twilio-internal` org.

- [x] **Step 2: Add all team members as Write collaborators**

  17 members invited with Write access via:
  ```bash
  gh api repos/ugupta-twilio/risk_analytics_repo/collaborators/<username> \
    --method PUT --field permission="push"
  ```

  Members: LeroyTang, ssaiesh, SahanaS18, rolims, maunaAR, kbhat27s, klalwani01,
  deekshatiwari1, shubhabhat2, PriyankaTwilio, pviplove, skuanar, ayusrivastava30,
  Kumud113, ssasank-lab, lkadam-twilio, lschanne-twilio

  **Note:** Invitations pending — each analyst must accept via email or
  `github.com/ugupta-twilio/risk_analytics_repo/invitations`

---

## Task 5: Configure Branch Protection on `main`

**Files:** GitHub branch protection settings (no repo files changed).

- [x] **Step 1: Apply branch protection rules**

  ```bash
  gh api repos/ugupta-twilio/risk_analytics_repo/branches/main/protection \
    --method PUT \
    --input - <<'EOF'
  {
    "required_status_checks": null,
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1,
      "dismiss_stale_reviews": true
    },
    "restrictions": null
  }
  EOF
  ```

- [x] **Step 2: Verified protection is active**

  ```json
  {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "force_push_allowed": false
  }
  ```

---

## Task 6: Add SageMaker Studio Auto-Sync (Case 2)

**Files:**
- `sagemaker/setup.sh`
- `sagemaker/README.md`

### How it works (ticket-branch mode)

Every analyst runs `setup.sh` once in their SageMaker Studio terminal. It:
1. Generates an SSH key (`~/.ssh/id_ed25519_github`) and configures `~/.ssh/config`
2. Tests GitHub SSH auth before proceeding
3. Clones the repo to `~/risk-analytics`
4. Installs a JupyterLab post-save hook in `~/.jupyter/jupyter_server_config.py`

After setup + Studio restart, saving any file inside `~/risk-analytics/` triggers the hook which:
- Walks up the folder tree to find a `.sync-branch` file
- Reads the target branch name from it (e.g. `feature/RISK-3016`)
- Auto-creates the branch from `main` if it doesn't exist on GitHub
- Runs `git add → git commit "auto: save <filename>" → git push` to that branch

Analysts create a `.sync-branch` file in their folder (e.g. `echo "feature/RISK-3016" > .sync-branch`) to activate sync for that ticket. No `.sync-branch` file = no sync (skip silently).

### Key implementation details

- `read -rp "..." < /dev/tty` — works correctly when script is run via `curl | bash`
- `{ ssh -T git@github.com 2>&1 || true; } | grep -q "..."` — handles ssh's non-zero exit on success
- `chmod 700 ~/.ssh` and `chmod 600 ~/.ssh/config` — SSH permission requirements
- `Host github.com` conflict detection — warns if a config block already exists
- `os_path.startswith(repo_dir + os.sep)` — prevents false-positive matches on similarly-named dirs
- `except Exception as e` — logs to `~/.jupyter/sync-errors.log`, never blocks a save

- [x] **Step 1: Create `sagemaker/setup.sh`** (executable, `chmod +x`)
- [x] **Step 2: Create `sagemaker/README.md`**
- [x] **Step 3: Commit and push**

  ```bash
  git add sagemaker/
  git commit -m "feat: add SageMaker Studio auto-sync setup (post-save hook)"
  git push origin main
  ```

### Analyst setup command

```bash
curl -fsSL https://raw.githubusercontent.com/ugupta-twilio/risk_analytics_repo/main/sagemaker/setup.sh \
  | bash -s <your-github-username>
```

---

## Task 7: End-to-End Verification

- [x] **Step 1: Repo structure on GitHub** — all 9 files present on `main`
- [x] **Step 2: Branch protection** — 1 required review, stale dismissal, force push blocked
- [x] **Step 3: Collaborator invitations** — 17 Write invites sent and pending

**Remaining manual steps:**
1. Analysts accept their GitHub collaboration invitations
2. Each analyst runs the setup script in their SageMaker Studio terminal
3. Each analyst creates a `.sync-branch` file in their folder with the target branch name
4. After Studio space restart, verify a notebook save creates an `auto: save` commit on the ticket branch

**Note on leads.json:** Registering a lead in `.github/leads.json` is **optional but recommended** for larger tickets. Without it, there is no designated reviewer for ticket-level files and the `path-check` CI will block any non-analyst from touching the ticket root. For small or short-lived tickets, skipping it is fine.

---

## Update Spec

Update `docs/superpowers/specs/2026-06-01-risk-analytics-github-repo-design.md`:

- Remove "SageMaker integration" from the **Out of Scope** section
- Add a **SageMaker Integration** section describing the auto-sync (post-save hook) approach
- Update repo name to `ugupta-twilio/risk_analytics_repo`
