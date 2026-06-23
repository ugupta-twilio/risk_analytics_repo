# SageMaker Studio — Auto-Sync Setup Guide

> **What this does in plain English:**
> Every time you save a notebook in SageMaker Studio, it is automatically saved to GitHub — no manual git commands needed. Your work is always backed up and shared with the team the moment you hit Ctrl+S.
>
> Setup takes about 10 minutes and you only do it once.

---

## Which path are you on?

- 🆕 **New to this system?** Follow the guide from top to bottom.
- 🔄 **Already set up, just want notebooks to auto-save to main?** Jump to [Part 3 — Enable Direct-to-Main for Sagemaker Notebooks](#part-3--enable-direct-to-main-for-sagemaker-notebooks).
- 🔄 **Set up before June 2026?** You need a one-time hook update — jump to [Updating an Existing Setup](#updating-an-existing-setup).

---

## Before You Start

Make sure you have all of these before opening a terminal:

- [ ] **A GitHub account** — if you don't have one, create one at [github.com](https://github.com)
- [ ] **Accepted the repo invite** — check your email for an invitation from `ugupta-twilio/risk_analytics_repo`, or visit [github.com/ugupta-twilio/risk_analytics_repo/invitations](https://github.com/ugupta-twilio/risk_analytics_repo/invitations)
- [ ] **Your GitHub username matches your analyst folder name exactly** — for example, if your GitHub username is `kbhat27s`, your folder in the repo must also be called `kbhat27s` (case-sensitive)
- [ ] **Access to a terminal in SageMaker Studio** — go to **File → New → Terminal** inside Studio
- [ ] **Admin bypass added** — ask your repo admin to run one command that allows your notebooks to save directly to `main` (see [Admin Step: Add Bypass](#admin-step-add-bypass) below). You don't run this yourself.

---

## Admin Step: Add Bypass

> **This is for repo admins only.** Analysts do not run this command.

Before an analyst's first notebook save can reach `main`, add their GitHub account to the bypass list:

```bash
gh api repos/ugupta-twilio/risk_analytics_repo/branches/main/protection/restrictions/users \
  --method POST \
  --field users[]="<github-username>"
```

Replace `<github-username>` with the analyst's exact GitHub username. This is a **one-time step per analyst**.

---

## Part 1 — One-Time Setup

### Step 1: Open a Terminal in SageMaker Studio

In SageMaker Studio, click **File → New → Terminal**.

A terminal window will open at the bottom of your screen.

---

### Step 2: Run the Setup Script

Copy and paste this command into the terminal. Replace `<your-github-username>` with your actual GitHub username (e.g. `kbhat27s`):

```bash
curl -fsSL https://raw.githubusercontent.com/ugupta-twilio/risk_analytics_repo/main/sagemaker/setup.sh \
  | bash -s <your-github-username>
```

**What happens next:** The script will generate an SSH key (your personal "ID card" for GitHub) and print it on screen. It will then pause and wait for you.

You will see something like this:

```
==> Setting up SSH key...
==> PUBLIC KEY — add this to your GitHub account before continuing:
    github.com → Settings → SSH and GPG keys → New SSH key

ssh-ed25519 AAAA...long string... kbhat27s@twilio-sagemaker

Press ENTER once you have added the key to GitHub...
```

**Do not press ENTER yet.** Go to Step 3 first.

---

### Step 3: Add Your Key to GitHub

This step tells GitHub "this SageMaker machine belongs to me." You only do this once.

1. **Copy** the entire public key printed in the terminal — it starts with `ssh-ed25519` and ends with your username
2. Open a new browser tab and go to [github.com/settings/ssh/new](https://github.com/settings/ssh/new)
3. Fill in the form:
   - **Title:** `SageMaker Studio` (so you remember what this key is for)
   - **Key type:** `Authentication Key`
   - **Key:** paste the key you copied
4. Click **Add SSH key**
5. Go back to the SageMaker terminal and press **ENTER**

---

### Step 4: Let the Script Finish

After you press ENTER, the script automatically:

1. **Verifies your GitHub connection** — you should see:
   ```
   ==> Testing GitHub SSH connection...
       Auth OK.
   ```
   If you see an error here, see [Troubleshooting](#troubleshooting).

2. **Clones the repository** to `~/risk-analytics/` on your SageMaker machine

3. **Installs the auto-save hook** — this is the part that makes every notebook save automatically go to GitHub

When it's done you'll see:
```
==> Setup complete.
    Repo: /home/sagemaker-user/risk-analytics
```

---

### Step 5: Restart Your Studio Space

**This step is required.** The auto-save hook only switches on after a restart.

In SageMaker Studio: **File → Shut Down → Restart**

Wait for Studio to come back up before continuing.

---

## Part 2 — Enable Auto-Sync for a Ticket

After restarting, you need to tell the system which GitHub branch to push your work to. This is done with a small file called `.sync-branch`.

### Step 6: Create Your Analyst Folder

If you haven't already created your folder for this ticket, do it now:

```bash
cd ~/risk-analytics
mkdir -p projects/GM/RISK-3016/<your-github-username>
cp projects/_template/README.md projects/GM/RISK-3016/<your-github-username>/README.md
touch projects/GM/RISK-3016/<your-github-username>/__init__.py
```

Replace `RISK-3016` with your ticket number and `<your-github-username>` with your username.

---

### Step 7: Create the `.sync-branch` File

This one-line file tells the system which branch to push your work to.

```bash
echo "feature/RISK-3016" > ~/risk-analytics/projects/GM/RISK-3016/<your-github-username>/.sync-branch
```

- Replace `feature/RISK-3016` with your actual ticket branch name
- If the branch doesn't exist on GitHub yet, the system **creates it automatically** on your first save
- To switch to a different ticket later, just update this file with the new branch name

---

### Step 8: Verify It's Working

1. Open any notebook inside your analyst folder in JupyterLab
2. Make a small change (e.g. add a comment in a cell)
3. Save with **Ctrl+S**
4. In the terminal, check that a commit appeared:

```bash
cd ~/risk-analytics
git log --oneline -3
```

You should see something like:
```
a1b2c3d auto: save my-notebook.ipynb
```

5. Confirm it pushed to GitHub:

```bash
git log --oneline origin/feature/RISK-3016 -3
```

If you see the commit there, you're all set. Every save from now on is automatic.

---

## Part 3 — Enable Direct-to-Main for Sagemaker Notebooks

This part is for `.ipynb` files saved inside a special `sagemaker/` subfolder. These notebooks push **directly to `main`** on every save — no PR or review step needed.

### How It Works

| File location | Where it saves |
|---|---|
| `projects/.../you/sagemaker/notebook.ipynb` | Directly to `main` |
| `projects/.../you/analysis.ipynb` | To your feature branch (via `.sync-branch`) |
| `projects/.../you/sagemaker/helper.py` | Nowhere (ignored) |

### Step 9: Create Your Sagemaker Folder

```bash
mkdir -p ~/risk-analytics/projects/GM/RISK-3016/<your-github-username>/sagemaker
```

The folder name must be exactly `sagemaker` (lowercase). Do not nest it deeper — it must sit directly inside your `<username>/` folder.

### Step 10: Create a Notebook and Save

1. In JupyterLab, open `projects/GM/RISK-3016/<your-username>/sagemaker/`
2. Create a new notebook (`.ipynb` file)
3. Make any change and save with **Ctrl+S**
4. Verify it landed on `main`:

```bash
cd ~/risk-analytics
git log --oneline origin/main -3
```

Expected top line:
```
a1b2c3d auto: save my-notebook.ipynb
```

> **Remember:** The admin bypass must be in place before this works (see [Admin Step: Add Bypass](#admin-step-add-bypass)). If saves are not appearing on `main`, check the troubleshooting table below.

---

## Part 4 — Opening a PR to Main (for feature branch work)

When your analysis in a feature branch is ready to share:

1. Go to [github.com/ugupta-twilio/risk_analytics_repo](https://github.com/ugupta-twilio/risk_analytics_repo)
2. You'll see a yellow banner: **"feature/RISK-3016 had recent pushes — Compare & pull request"** — click it
3. Fill in the PR template:
   - What you changed and why
   - How someone can verify it
   - Check all checklist items
4. Submit — you and the ticket lead are automatically assigned as reviewers
5. Once approved, merge to `main`

> **Note:** An automated check (`path-check`) will verify your PR only touches files inside your own folder. If it fails, the error message will tell you exactly which file is out of scope.

---

## Updating an Existing Setup

If you ran the setup script before June 2026, you need to re-run it once to pick up the new sagemaker routing logic:

```bash
curl -fsSL https://raw.githubusercontent.com/ugupta-twilio/risk_analytics_repo/main/sagemaker/setup.sh \
  | bash -s <your-github-username>
```

Then restart your Studio space. You can verify the update was applied:

```bash
grep "_is_sagemaker_path" ~/.jupyter/jupyter_server_config.py
```

If it prints a line of code, the update is in place. If it prints nothing, re-run the setup script.

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `Permission denied (publickey)` when running SSH | Public key not added to GitHub | Copy the key from `cat ~/.ssh/id_ed25519_github.pub` and add it at [github.com/settings/ssh/new](https://github.com/settings/ssh/new) |
| `ssh -T` hangs with no output | SageMaker blocks port 22 | Try `ssh -T -p 443 git@ssh.github.com` — if this works, ask your admin to update `~/.ssh/config` to use port 443 |
| Script exits with `ERROR: SSH auth failed` | Key not on GitHub yet when ENTER was pressed | Re-run the script; add the key to GitHub before pressing ENTER |
| No `auto: save` commits after saving | Studio not restarted after setup | Shut down and restart your Studio space |
| Saves going to wrong branch | `.sync-branch` has wrong branch name | Run: `cat ~/risk-analytics/projects/.../your-username/.sync-branch` and update if wrong |
| Commits appear locally but not on GitHub | Push silently failed | Check `cat ~/.jupyter/sync-errors.log` for the error |
| `sagemaker/` notebook saves not appearing on `main` | Admin bypass not added | Ask your repo admin to run the `gh api` bypass command from [Admin Step: Add Bypass](#admin-step-add-bypass) |
| PR blocked by `path-check` CI | PR touches files outside your folder | Read the CI error — it lists exactly which files are out of scope |
| Folder name mismatch error in CI | GitHub username and folder name don't match | Rename your folder to match your GitHub username exactly (case-sensitive) |
| Hook not found after running setup | Config file missing the hook | Run `grep "risk_analytics_auto_sync" ~/.jupyter/jupyter_server_config.py` — if empty, re-run setup |

---

## Quick Reference

### Key file locations

| File | What it is |
|---|---|
| `~/risk-analytics/` | Your local copy of the repo |
| `~/.ssh/id_ed25519_github` | Your private SSH key — never share this |
| `~/.ssh/id_ed25519_github.pub` | Your public SSH key — this goes on GitHub |
| `~/.jupyter/jupyter_server_config.py` | JupyterLab config — contains the auto-save hook |
| `~/.jupyter/sync-errors.log` | Error log — check here if saves stop working |
| `projects/.../<username>/.sync-branch` | One-line file with the target branch name |

### Manual save (if auto-sync stops working)

```bash
cd ~/risk-analytics
git status
git add projects/GM/RISK-3016/<username>/my-notebook.ipynb
git commit -m "manual: update analysis"
git push origin feature/RISK-3016
```

### Two auto-sync modes at a glance

| Mode | Trigger | Destination | Needs `.sync-branch`? |
|---|---|---|---|
| Feature branch sync | Save any file in your analyst folder | Your feature branch | Yes |
| Direct-to-main sync | Save a `.ipynb` in `<username>/sagemaker/` | `main` directly | No |
