# Risk Analytics

Code repository for the Twilio Risk Analytics (RA) team.

**GitHub repo:** [ugupta-twilio/risk_analytics_repo](https://github.com/ugupta-twilio/risk_analytics_repo)

---

## Table of Contents

1. [Repository Structure](#repository-structure)
2. [Getting Started](#getting-started)
3. [Folder Structure Rules](#folder-structure-rules)
4. [SageMaker Studio Auto-Sync](#sagemaker-studio-auto-sync)
5. [Access Control](#access-control)
6. [Contributing](#contributing)
7. [Team](#team)

---

## Repository Structure

```
risk-analytics/
├── projects/
│   ├── _template/              # Copy this when starting a new project
│   └── <area>/                 # Business area (e.g. GM, FRAUD, CREDIT)
│       └── <TICKET-ID>/        # One folder per ticket (e.g. RISK-3016)
│           └── <username>/     # Your personal work folder (named after your GitHub username)
│               ├── README.md       # Required — describe your project
│               ├── __init__.py     # Required — empty file
│               ├── .sync-branch    # Required — target branch for SageMaker auto-sync
│               └── <your files>    # Notebooks, scripts, etc.
├── shared/
│   └── utils/                  # Shared helper code reused across projects
├── sagemaker/
│   ├── setup.sh                # Run once in SageMaker Studio to enable auto-sync
│   └── README.md               # Full SageMaker setup guide
├── scripts/
│   └── update_codeowners.py    # Auto-regenerates CODEOWNERS from folder structure
└── .github/
    ├── CODEOWNERS              # Auto-assigns reviewers per folder
    ├── leads.json              # Optional: maps ticket folders to their leads
    └── workflows/
        ├── path-check.yml          # CI: blocks PRs that touch unauthorized folders
        └── update-codeowners.yml   # CI: auto-updates CODEOWNERS on merge
```

---

## Getting Started

### Step 1 — Accept your collaborator invitation

Check your email or visit [github.com/ugupta-twilio/risk_analytics_repo/invitations](https://github.com/ugupta-twilio/risk_analytics_repo/invitations) and accept the Write access invite.

### Step 2 — Set up SageMaker Studio auto-sync (one time per Studio profile)

Run this in your SageMaker Studio terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/ugupta-twilio/risk_analytics_repo/main/sagemaker/setup.sh \
  | bash -s <your-github-username>
```

This sets up SSH authentication to GitHub and installs a post-save hook. After a Studio space restart, every notebook save inside your ticket folder is automatically committed and pushed to your feature branch — no manual git needed.

See [sagemaker/README.md](sagemaker/README.md) for the full step-by-step guide.

### Step 3 — Join a ticket

1. Create a branch: `setup/<your-username>-joins-RISK-XXXX`
2. Create your analyst folder: `projects/<area>/RISK-XXXX/<your-github-username>/` with these three files:

   | File | Contents |
   |---|---|
   | `README.md` | Copy from `projects/_template/README.md` and fill in your project details |
   | `__init__.py` | Empty file |
   | `.sync-branch` | One line: the feature branch name, e.g. `feature/RISK-XXXX` |

   ```bash
   # Example — run from inside ~/risk-analytics/
   mkdir -p projects/GM/RISK-3016/<your-github-username>
   cp projects/_template/README.md projects/GM/RISK-3016/<your-github-username>/README.md
   touch projects/GM/RISK-3016/<your-github-username>/__init__.py
   echo "feature/RISK-3016" > projects/GM/RISK-3016/<your-github-username>/.sync-branch
   ```

3. Open a PR — CI validates the folder name matches your GitHub username automatically
4. The ticket lead (or repo admin) reviews and merges
5. After merge: restart your Studio space, then every save auto-pushes to `feature/RISK-3016`

> **Important:** Your folder name must exactly match your GitHub username (case-sensitive).

---

## Folder Structure Rules

### Hierarchy

```
projects/
└── <area>/                        # Level 1 — Business area (e.g. GM)
    └── <TICKET-ID>/               # Level 2 — Work ticket (e.g. RISK-3016)
        └── <github-username>/     # Level 3 — Analyst personal folder
            └── <your files>       # Level 4 — Notebooks, scripts, data refs
```

### Who can create what

| Folder level | Example | Who creates it | How |
|---|---|---|---|
| `projects/<area>/` | `projects/GM/` | **Repo admin only** (`@ugupta-twilio`) | Open a PR directly; analysts cannot create new area folders |
| `projects/<area>/<TICKET-ID>/` | `projects/GM/RISK-3016/` | **Ticket lead** | Open a PR on branch `setup/ticket-RISK-XXXX`; optionally register as lead in `.github/leads.json` |
| `projects/<area>/<TICKET-ID>/<username>/` | `projects/GM/RISK-3016/kbhat27s/` | **Analyst (self-service)** | Open a PR on branch `setup/<username>-joins-<TICKET>`; CI validates folder name = GitHub username |
| `shared/utils/<subfolder>/` | `shared/utils/fraud/` | **Repo admin or ticket lead** | Open a PR; changes here affect all analysts |
| `.github/` files | `leads.json`, `CODEOWNERS` | **Repo admin only** | CI blocks non-admin PRs touching `.github/` |

### Naming conventions

| Level | Rule | Valid examples |
|---|---|---|
| Area | Short uppercase abbreviation | `GM`, `FRAUD`, `CREDIT` |
| Ticket ID | `WORD-NNNN` uppercase, matching your JIRA ticket | `RISK-3016`, `RISK-3017` |
| Username folder | **Exact GitHub username** — case-sensitive, no substitutions | `kbhat27s`, `klalwani01` |
| Files / notebooks | Lowercase with hyphens or underscores | `model_v2.ipynb`, `feature-engineering.py` |

### Creating a new ticket folder (ticket lead)

1. Create a branch: `setup/ticket-RISK-XXXX`
2. Create `projects/<area>/RISK-XXXX/` with a `README.md` describing the ticket goal
3. *(Optional but recommended)* Register yourself as lead in `.github/leads.json`:
   ```json
   "projects/<area>/RISK-XXXX": "<your-github-username>"
   ```
   **Why:** When registered, CODEOWNERS auto-assigns you as required reviewer on every PR touching this ticket, and CI allows you to write ticket-level shared files. Without this, there is no designated reviewer — acceptable for small tickets, but worth adding for longer-running work.
4. Open a PR — repo admin reviews and merges
5. Announce the ticket so analysts can self-provision their folders

---

## SageMaker Studio Auto-Sync

Auto-sync means every notebook save in SageMaker Studio automatically commits and pushes to your feature branch on GitHub. No manual `git add`, `git commit`, or `git push` needed.

**How it works:**

1. Each analyst folder contains a `.sync-branch` file with one line — the target branch name (e.g. `feature/RISK-3016`)
2. On every save, the post-save hook walks up the folder tree to find the nearest `.sync-branch` file
3. It checks out that branch (creating it from `main` if it doesn't exist yet), commits the file, and pushes
4. If no `.sync-branch` is found, the save is skipped silently

**To enable auto-sync for your folder:**

```bash
echo "feature/RISK-3016" > ~/risk-analytics/projects/GM/RISK-3016/<your-username>/.sync-branch
```

For the full setup guide including SSH key setup, troubleshooting, and how to open a PR to `main`, see [sagemaker/README.md](sagemaker/README.md).

---

## Access Control

This repo enforces folder-level access via GitHub Actions CI and CODEOWNERS.

| Who | Can write to |
|---|---|
| Ticket lead (if registered in `leads.json`) | Entire `projects/<area>/<ticket>/` folder |
| Analyst | Only their own `projects/<area>/<ticket>/<username>/` folder |
| Repo admin (`@ugupta-twilio`) | `.github/` config files and `shared/utils/` |

**Enforcement mechanism:**

- Every PR triggers the `path-check` CI workflow. If your PR touches files outside your allowed folder, CI fails and merge is blocked.
- CODEOWNERS auto-assigns the ticket lead (if registered) and you as required reviewers on PRs touching your folder.
- When a new analyst folder lands on `main`, the `update-codeowners` workflow auto-opens a PR to keep CODEOWNERS current.

---

## Contributing

- All changes to `main` require a PR with at least **1 approval**
- PRs may only touch files inside your own `<username>/` folder, or ticket-level files if you are the registered lead
- Do **not** commit raw data files or credentials — store data in S3 and reference the path
- Do **not** commit `.env` files — see `.gitignore` for the full exclusion list
- Run your code end-to-end before merging — no broken notebooks on `main`

---

## Team

| Role | GitHub |
|---|---|
| Repo admin / RA Lead | [@ugupta-twilio](https://github.com/ugupta-twilio) |
