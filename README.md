# Risk Analytics

Code repository for the Twilio Risk Analytics (RA) team.

**GitHub repo:** [ugupta-twilio/risk_analytics_repo](https://github.com/ugupta-twilio/risk_analytics_repo)

---

## Repository Structure

```
risk-analytics/
├── projects/
│   ├── _template/          # Copy this when starting a new project
│   └── <area>/
│       └── <TICKET-ID>/    # One folder per ticket (e.g. RISK-3016)
│           └── <username>/ # Your personal work folder — named after your GitHub username
├── shared/
│   └── utils/              # Shared helper code reused across projects
├── sagemaker/              # SageMaker Studio auto-sync setup
│   ├── setup.sh            # Run this once in SageMaker Studio to enable auto-sync
│   └── README.md           # Step-by-step guide
├── scripts/
│   └── update_codeowners.py # Auto-regenerates CODEOWNERS from folder structure
└── .github/
    ├── CODEOWNERS          # Auto-assigns reviewers per folder
    ├── leads.json          # Maps ticket folders to their leads
    └── workflows/
        ├── path-check.yml          # CI: blocks PRs that touch unauthorized folders
        └── update-codeowners.yml   # CI: auto-updates CODEOWNERS on merge
```

---

## Getting Started

### 1. Accept your collaborator invitation

Check your email or go to [github.com/ugupta-twilio/risk_analytics_repo/invitations](https://github.com/ugupta-twilio/risk_analytics_repo/invitations) and accept the Write access invite.

### 2. Set up SageMaker Studio auto-sync (one time)

See [sagemaker/README.md](sagemaker/README.md). After setup, every notebook save inside `~/risk-analytics/` is automatically committed and pushed to your personal branch — no manual git needed.

### 3. Join a ticket

To start working on a ticket (e.g. RISK-3016):

1. Create a branch: `setup/<your-username>-joins-RISK-3016`
2. Add your folder: `projects/GM/RISK-3016/<your-github-username>/` containing:
   - `README.md` (copy from `projects/_template/README.md`)
   - `__init__.py` (empty)
3. Open a PR — CI validates the folder name matches your GitHub username automatically
4. The ticket lead reviews and merges

---

## Folder Structure Rules

The repo uses a strict 4-level hierarchy under `projects/`. Each level has a defined owner, naming convention, and creation process.

### Level overview

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
| `projects/<area>/` | `projects/GM/` | **Repo admin only** (`@ugupta-twilio`) | Open a PR directly; no analyst can create new area folders |
| `projects/<area>/<TICKET-ID>/` | `projects/GM/RISK-3016/` | **Ticket lead** | Open a PR on branch `setup/ticket-RISK-XXXX`; update `.github/leads.json` to register yourself as lead |
| `projects/<area>/<TICKET-ID>/<username>/` | `projects/GM/RISK-3016/kbhat27s/` | **Analyst (self-service)** | Open a PR on branch `setup/<username>-joins-<TICKET>`; CI validates the folder name matches your GitHub username |
| `shared/utils/<subfolder>/` | `shared/utils/fraud/` | **Repo admin or ticket lead** | Open a PR; changes here affect all analysts |
| `.github/` files | `leads.json`, `CODEOWNERS` | **Repo admin only** | CI blocks non-admin PRs touching `.github/` |

### Naming conventions

| Folder level | Rule | Examples |
|---|---|---|
| Area | Short uppercase abbreviation | `GM`, `FRAUD`, `CREDIT` |
| Ticket ID | `WORD-NNNN` uppercase, matching the JIRA ticket | `RISK-3016`, `RISK-3017` |
| Username | **Exact GitHub username** — case-sensitive | `kbhat27s`, `klalwani01` |
| Files/notebooks | Lowercase with hyphens or underscores | `model_v2.ipynb`, `feature-engineering.py` |

### Step-by-step: creating a new ticket folder (ticket lead)

1. Create a branch: `setup/ticket-RISK-XXXX`
2. Create the folder `projects/<area>/RISK-XXXX/` with a `README.md` (describe the ticket goal)
3. Add an entry to `.github/leads.json`:
   ```json
   "projects/<area>/RISK-XXXX": "<your-github-username>"
   ```
4. Open a PR — repo admin reviews and merges
5. Announce the ticket to analysts so they can self-provision their personal folders

### Step-by-step: joining a ticket as an analyst

1. Create a branch: `setup/<your-username>-joins-RISK-XXXX`
2. Create your folder: `projects/<area>/RISK-XXXX/<your-github-username>/` with:
   - `README.md` (copy from `projects/_template/README.md`)
   - `__init__.py` (empty)
   - `.sync-branch` — one line containing your target branch name, e.g. `feature/RISK-XXXX`
     ```bash
     echo "feature/RISK-XXXX" > projects/<area>/RISK-XXXX/<your-github-username>/.sync-branch
     ```
3. Open a PR — `path-check` CI auto-validates the folder name matches your GitHub username
4. Ticket lead reviews and merges; CODEOWNERS is auto-updated on merge
5. In SageMaker Studio, after setup: every save inside your folder auto-pushes to `feature/RISK-XXXX`

> **Rule:** You may only create a folder whose name is your exact GitHub username. Creating a folder under someone else's username will be blocked by CI.

---

## Access Control

This repo enforces **folder-level access** via GitHub Actions CI and CODEOWNERS:

| Who | Can write to |
|---|---|
| Ticket lead | Entire `projects/<area>/<ticket>/` folder |
| Analyst | Only their own `projects/<area>/<ticket>/<username>/` folder |
| Repo admin (`@ugupta-twilio`) | `.github/` config files |

**How it works:**

- Every PR runs the `path-check` CI workflow. If your PR touches files outside your allowed folder, the check fails and merge is blocked.
- CODEOWNERS auto-assigns the ticket lead and you as required reviewers on any PR touching your folder.
- When a new analyst folder is detected on `main`, the `update-codeowners` workflow opens a follow-up PR to keep CODEOWNERS current.

> **Important:** Your folder name must exactly match your GitHub username. E.g. if your GitHub username is `kbhat27s`, your folder must be `projects/GM/RISK-3016/kbhat27s/`.

---

## Contributing

- All changes to `main` require a PR with at least 1 approval
- PRs may only touch files inside your own `<username>/` folder (or ticket-level files if you are the lead)
- Do not commit data files, credentials, or `.env` files — store data in S3
- Run your code before merging — no broken notebooks on `main`

---

## Team

| Role | GitHub |
|---|---|
| Repo admin / RA Lead | [@ugupta-twilio](https://github.com/ugupta-twilio) |
