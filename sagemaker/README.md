# SageMaker Studio — Auto-Sync Setup Guide

After completing this one-time setup, every notebook save inside SageMaker Studio
is automatically committed and pushed to GitHub. No manual git commands needed.

## Prerequisites

- GitHub account added as a collaborator to [ugupta-twilio/risk_analytics_repo](https://github.com/ugupta-twilio/risk_analytics_repo)
- Your GitHub username must match your folder name inside `projects/` (e.g. username `kbhat27s` → folder `projects/GM/RISK-3016/kbhat27s/`)

---

## Setup (run once per Studio user profile)

Open a terminal in SageMaker Studio (File → New → Terminal):

```bash
curl -fsSL https://raw.githubusercontent.com/ugupta-twilio/risk_analytics_repo/main/sagemaker/setup.sh \
  | bash -s <your-github-username>
```

The script will:
1. Generate an SSH key and print the public key for you to add to GitHub
2. Wait for you to confirm the key is added, then verify the connection
3. Clone the repo to `~/risk-analytics`
4. Create your personal auto-sync branch `auto/<your-github-username>`
5. Install a JupyterLab post-save hook in `~/.jupyter/jupyter_server_config.py`

After the script finishes, **restart your Studio space** (File → Shut Down → restart)
so the post-save hook takes effect.

---

## How auto-sync works

Auto-sync is driven by a `.sync-branch` file you place in your analyst folder. The hook reads this file on every save to know which branch to push to.

- Every time you save a file inside `~/risk-analytics/`, the hook:
  1. Walks up the folder tree to find the nearest `.sync-branch` file
  2. Reads the target branch name from it (e.g. `feature/RISK-3016`)
  3. If the branch doesn't exist on GitHub yet — creates it from `main` automatically
  4. Runs: `git add <file>` → `git commit -m "auto: save <filename>"` → `git push`
- Files saved outside `~/risk-analytics/` are not synced
- Files inside `~/risk-analytics/` with no `.sync-branch` in their folder tree are skipped silently
- Errors are logged to `~/.jupyter/sync-errors.log` and never block your save

---

## Setting up auto-sync for a ticket

After running `setup.sh` and restarting your Studio space:

1. Create your analyst folder if it doesn't exist:
   ```
   projects/GM/RISK-3016/<your-github-username>/
   ```
2. Create a `.sync-branch` file inside it with your target branch name:
   ```bash
   echo "feature/RISK-3016" > ~/risk-analytics/projects/GM/RISK-3016/<your-github-username>/.sync-branch
   ```
3. That's it — every save inside that folder now auto-pushes to `feature/RISK-3016`

To switch to a different branch (e.g. for a new ticket), update the `.sync-branch` file:
```bash
echo "feature/RISK-3017" > ~/risk-analytics/projects/GM/RISK-3017/<your-github-username>/.sync-branch
```

---

## Opening a PR to main

1. Go to [github.com/ugupta-twilio/risk_analytics_repo](https://github.com/ugupta-twilio/risk_analytics_repo)
2. Click **"Compare & pull request"** on your `feature/<TICKET-ID>` branch
3. Fill in the PR template and submit
4. The ticket lead and you are auto-assigned as reviewers via CODEOWNERS

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Saves work but no commits appear on GitHub | Studio space not restarted after setup — shut down and restart |
| `Permission denied (publickey)` on setup | Public key not added to GitHub yet — re-run setup |
| `ssh -T` hangs | Try `ssh -T -p 443 git@ssh.github.com` — Studio may block port 22 |
| Hook installed but nothing pushes | Check `~/.jupyter/jupyter_server_config.py` contains the `risk_analytics_auto_sync` block |
| PR blocked by `path-check` CI | Your PR touches files outside your `<username>/` folder — check the CI error message |
| Folder name mismatch error | Your folder name must exactly match your GitHub username |
| Auto-sync not pushing | Check `.sync-branch` file exists and contains a valid branch name |
| Wrong branch being pushed to | Update the `.sync-branch` file with the correct branch name and save again |
| Branch creation failed | Check `~/.jupyter/sync-errors.log` for the error; verify GitHub SSH auth with `ssh -T git@github.com` |
