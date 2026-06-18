# SageMaker Studio — Auto-Sync Setup Guide

This guide walks you through connecting your SageMaker Studio environment to the
`risk_analytics_repo` GitHub repository so that every notebook save is automatically
committed and pushed to your feature branch. You only need to do this **once per
SageMaker Studio user profile**.

---

## What auto-sync does

When set up correctly:

- Every time you **save a file** (Ctrl+S) inside `~/risk-analytics/`, the system automatically:
  1. Stages the file: `git add <file>`
  2. Commits it: `git commit -m "auto: save <filename>"`
  3. Pushes it to your feature branch on GitHub: `git push`
- The target branch is read from a `.sync-branch` file in your analyst folder
- If the target branch doesn't exist on GitHub yet, it is **created automatically** from `main`
- Files saved **outside** `~/risk-analytics/` are never touched
- Any git errors are written to `~/.jupyter/sync-errors.log` and **never block your save**

---

## SageMaker Notebook Auto-Sync to Main

`.ipynb` files saved inside your `<username>/sagemaker/` folder are committed and pushed
**directly to `main`** on every save — no PR or review required.

### Folder structure

Your notebook must be at this path:

```
projects/<area>/<ticket>/<username>/sagemaker/<notebook>.ipynb
```

Example: `projects/GM/RISK-3016/kbhat/sagemaker/analysis.ipynb`

### Rules

- Only `.ipynb` files sync to main. All other file types (`.py`, `.csv`, etc.)
  saved in the `sagemaker/` folder are silently ignored.
- The folder must be named exactly `sagemaker` (lowercase).
- The folder must sit directly inside your `<username>/` folder — not nested deeper.
- A `.sync-branch` file is **not** needed inside the `sagemaker/` folder.

### Prerequisite: admin bypass

Before your first notebook save can reach `main`, a repo admin must add your GitHub
account to the `main` branch protection bypass list. Ask your repo admin to run:

```bash
gh api repos/ugupta-twilio/risk_analytics_repo/branches/main/protection/restrictions/users \
  --method POST \
  --field users[]="<your-github-username>"
```

This is a **one-time step per analyst**.

### Existing users: hook update

If you set up SageMaker auto-sync before June 2026, re-run the setup script to pick up the new routing logic:

```bash
curl -fsSL https://raw.githubusercontent.com/ugupta-twilio/risk_analytics_repo/main/sagemaker/setup.sh \
  | bash -s <your-github-username>
```

Then restart your Studio space.

---

## Prerequisites

Before running setup, confirm the following:

- [ ] You have a GitHub account
- [ ] You have accepted the collaborator invite for `ugupta-twilio/risk_analytics_repo`
  (check email or visit [github.com/ugupta-twilio/risk_analytics_repo/invitations](https://github.com/ugupta-twilio/risk_analytics_repo/invitations))
- [ ] Your GitHub username **exactly matches** your analyst folder name in the repo
  (e.g. GitHub username `kbhat27s` → folder must be `projects/GM/RISK-3016/kbhat27s/`)
- [ ] You have access to a terminal in SageMaker Studio
  (File → New → Terminal)

---

## Part 1 — Run the Setup Script

### Step 1: Open a terminal in SageMaker Studio

In SageMaker Studio: **File → New → Terminal**

### Step 2: Run the setup script

```bash
curl -fsSL https://raw.githubusercontent.com/ugupta-twilio/risk_analytics_repo/main/sagemaker/setup.sh \
  | bash -s <your-github-username>
```

Replace `<your-github-username>` with your actual GitHub username, e.g.:

```bash
curl -fsSL https://raw.githubusercontent.com/ugupta-twilio/risk_analytics_repo/main/sagemaker/setup.sh \
  | bash -s kbhat27s
```

### What the script does (step by step)

The script runs 4 operations:

**1. Generates an SSH key**

Creates a new SSH key pair at `~/.ssh/id_ed25519_github` (if one doesn't already exist).
This key is stored on SageMaker's EFS storage, so it **persists across Studio session restarts**
— you only generate it once.

```
==> Setting up SSH key...
Key generated at /home/sagemaker-user/.ssh/id_ed25519_github
```

**2. Prints your public key and waits**

The script prints your public key and pauses:

```
==> PUBLIC KEY — add this to your GitHub account before continuing:
    github.com → Settings → SSH and GPG keys → New SSH key

ssh-ed25519 AAAA... kbhat27s@twilio-sagemaker

Press ENTER once you have added the key to GitHub...
```

**At this point, do not press ENTER yet.** Go to the next step.

### Step 3: Add the public key to GitHub

1. Copy the entire public key printed in the terminal (starts with `ssh-ed25519`)
2. Go to [github.com/settings/ssh/new](https://github.com/settings/ssh/new)
3. Fill in:
   - **Title:** `SageMaker Studio` (or any label you recognise)
   - **Key type:** `Authentication Key`
   - **Key:** paste the copied public key
4. Click **Add SSH key**
5. Return to the SageMaker terminal and press **ENTER**

### Step 4: Script continues — verifies auth and clones the repo

After you press ENTER, the script automatically:

**Verifies GitHub authentication:**
```
==> Testing GitHub SSH connection...
    Auth OK.
```
If this fails, see the [Troubleshooting](#troubleshooting) section.

**Sets your git identity:**
```
==> Cloning repository...
```
Your git `user.name` is set to your GitHub username and `user.email` to `<username>@twilio.com`.

**Clones the repo** to `~/risk-analytics/` (or skips if already cloned).

**Installs the JupyterLab post-save hook** into `~/.jupyter/jupyter_server_config.py`.
This is the Python function that runs on every notebook save to do the auto-commit and push.

**Completion message:**
```
==> Setup complete.
    Repo: /home/sagemaker-user/risk-analytics

    To enable auto-sync for a ticket:
    1. Create your folder: projects/<area>/<TICKET-ID>/<your-github-username>/
    2. Add a .sync-branch file with the target branch, e.g.:
       echo 'feature/RISK-3016' > projects/GM/RISK-3016/kbhat27s/.sync-branch
    3. Restart your Studio space (File → Shut Down → restart)
    From then on, every save inside that folder auto-pushes to the branch.
```

### Step 5: Restart your Studio space

**This step is required.** The post-save hook only activates after a restart.

In SageMaker Studio: **File → Shut Down → Restart**

---

## Part 2 — Enable Auto-Sync for a Ticket

After completing Part 1 and restarting your Studio space, you need to tell the hook
which branch to push to. This is done with a `.sync-branch` file.

### Step 6: Create your analyst folder (if you haven't already)

If you haven't joined the ticket yet, create your folder in the repo:

```bash
cd ~/risk-analytics
mkdir -p projects/GM/RISK-3016/<your-github-username>
cp projects/_template/README.md projects/GM/RISK-3016/<your-github-username>/README.md
touch projects/GM/RISK-3016/<your-github-username>/__init__.py
```

### Step 7: Create the `.sync-branch` file

Inside your analyst folder, create a file named `.sync-branch` containing the
name of the feature branch you want to push to:

```bash
echo "feature/RISK-3016" > ~/risk-analytics/projects/GM/RISK-3016/<your-github-username>/.sync-branch
```

- The branch name must match the feature branch for your ticket (e.g. `feature/RISK-3016`)
- If this branch doesn't exist on GitHub yet, the hook will **create it automatically** from `main` on the first save
- To switch to a different branch later, simply update the file:
  ```bash
  echo "feature/RISK-3017" > ~/risk-analytics/projects/GM/RISK-3017/<your-github-username>/.sync-branch
  ```

### Step 8: Verify auto-sync is working

1. Open any notebook inside `~/risk-analytics/projects/GM/RISK-3016/<your-github-username>/`
2. Make a small change (e.g. add a comment)
3. Save with **Ctrl+S**
4. Check the commit appeared:

```bash
cd ~/risk-analytics
git log --oneline -3
```

Expected output (top line):
```
a1b2c3d auto: save my-notebook.ipynb
```

5. Verify it pushed to GitHub:

```bash
git log --oneline origin/feature/RISK-3016 -3
```

---

## Part 3 — Opening a PR to Main

When your analysis is ready to share with the team:

1. Go to [github.com/ugupta-twilio/risk_analytics_repo](https://github.com/ugupta-twilio/risk_analytics_repo)
2. You will see a banner: **"feature/RISK-3016 had recent pushes — Compare & pull request"**. Click it.
3. Fill in the PR template:
   - What this change does
   - How to validate
   - Check all checklist items
4. Submit the PR — the ticket lead and you are auto-assigned as reviewers via CODEOWNERS
5. Once approved, the PR can be merged to `main`

> **Note:** The `path-check` CI will verify your PR only touches files inside your own
> `<username>/` folder (or ticket-level files if you are the registered lead).
> If CI fails, read the error message — it will tell you exactly which file is out of scope.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ssh -T git@github.com` returns `Permission denied (publickey)` | Public key not added to GitHub | Repeat Step 3 — copy the key from `cat ~/.ssh/id_ed25519_github.pub` and add it at [github.com/settings/ssh/new](https://github.com/settings/ssh/new) |
| `ssh -T` hangs with no output | SageMaker blocks outbound SSH on port 22 | Try `ssh -T -p 443 git@ssh.github.com` — if this works, contact repo admin to update `~/.ssh/config` to use port 443 |
| Script exits with `ERROR: SSH auth failed` | Key not yet on GitHub when ENTER was pressed | Re-run the script; add the key before pressing ENTER |
| Auto-sync not pushing after restart | `.sync-branch` file missing or empty | Check `cat ~/risk-analytics/projects/.../your-username/.sync-branch` — it must contain a branch name |
| `git log` shows no new `auto: save` commits after saving | Studio space not restarted after setup | Shut down and restart your Studio space |
| Wrong branch being pushed to | `.sync-branch` has the wrong branch name | Update the file: `echo "feature/RISK-XXXX" > .sync-branch` |
| `auto: save` commits appear but not on GitHub | Push silently failed | Check `cat ~/.jupyter/sync-errors.log` for the error |
| PR blocked by `path-check` CI | PR touches files outside your `<username>/` folder | Read the CI error message — it lists the exact files causing the failure |
| Folder name mismatch CI error | GitHub username and folder name don't match exactly | Rename your folder to match your exact GitHub username (case-sensitive) |
| Hook not installed after running setup | `~/.jupyter/jupyter_server_config.py` missing the hook | Run `grep "risk_analytics_auto_sync" ~/.jupyter/jupyter_server_config.py` — if empty, re-run setup |
| `sagemaker/` notebook saves not appearing on `main` | Account not on branch bypass list | Ask your repo admin to run the `gh api` bypass command in the [SageMaker Notebook Auto-Sync to Main](#sagemaker-notebook-auto-sync-to-main) section above |

---

## Reference

### Key file locations

| File | Purpose |
|---|---|
| `~/risk-analytics/` | Local clone of the repo |
| `~/.ssh/id_ed25519_github` | Private SSH key (never share this) |
| `~/.ssh/id_ed25519_github.pub` | Public SSH key (add this to GitHub) |
| `~/.jupyter/jupyter_server_config.py` | JupyterLab config — contains the post-save hook |
| `~/.jupyter/sync-errors.log` | Auto-sync error log — check here if pushes stop working |
| `projects/.../<username>/.sync-branch` | Target branch for auto-sync (one line, branch name) |

### Manual git commands (if needed)

If auto-sync stops working or you need to push manually:

```bash
cd ~/risk-analytics
git status                          # see what's changed
git add projects/GM/RISK-3016/<username>/my-notebook.ipynb
git commit -m "manual: update analysis"
git push origin feature/RISK-3016
```
