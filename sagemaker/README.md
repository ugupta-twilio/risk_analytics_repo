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

- Every time you save a notebook inside `~/risk-analytics/`, the hook runs:
  `git add <file>` → `git commit -m "auto: save <filename>"` → `git push`
- Changes push to your personal branch `auto/<your-username>`, not `main`
- To share your work with the team, open a PR from your `auto/<username>` branch to `main`
- The PR must only touch files inside your own `projects/**/<username>/` folder — CI will block it otherwise
- Files saved outside `~/risk-analytics/` are not synced

---

## Opening a PR to main

1. Go to [github.com/ugupta-twilio/risk_analytics_repo](https://github.com/ugupta-twilio/risk_analytics_repo)
2. Click **"Compare & pull request"** on your `auto/<username>` branch
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
