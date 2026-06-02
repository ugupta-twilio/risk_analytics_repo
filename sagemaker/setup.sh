#!/usr/bin/env bash
# One-time setup: SSH key, repo clone, personal auto-sync branch,
# and JupyterLab post-save hook for automatic git push on every notebook save.
# Run once per SageMaker Studio user profile. All state persists on EFS.
set -euo pipefail

GITHUB_USER="${1:-}"
if [[ -z "$GITHUB_USER" ]]; then
  echo "Usage: bash setup.sh <your-github-username>"
  exit 1
fi

REPO_URL="git@github.com:ugupta-twilio/risk_analytics_repo.git"
REPO_DIR="$HOME/risk-analytics"
KEY_PATH="$HOME/.ssh/id_ed25519_github"
BRANCH="auto/${GITHUB_USER}"

# ── 1. SSH key ──────────────────────────────────────────────────────────────
echo "==> Setting up SSH key..."
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
if [[ ! -f "$KEY_PATH" ]]; then
  ssh-keygen -t ed25519 -C "${GITHUB_USER}@twilio-sagemaker" -f "$KEY_PATH" -N ""
fi

# Avoid duplicate or conflicting Host blocks in config
if grep -q "Host github.com" "$HOME/.ssh/config" 2>/dev/null; then
  echo "    WARN: ~/.ssh/config already has a 'Host github.com' block — skipping append."
  echo "    Verify it uses IdentityFile $KEY_PATH or update it manually."
elif ! grep -q "IdentityFile $KEY_PATH" "$HOME/.ssh/config" 2>/dev/null; then
  cat >> "$HOME/.ssh/config" <<EOF

Host github.com
  HostName github.com
  User git
  IdentityFile $KEY_PATH
  IdentitiesOnly yes
EOF
  chmod 600 "$HOME/.ssh/config"
fi

echo ""
echo "==> PUBLIC KEY — add this to your GitHub account before continuing:"
echo "    github.com → Settings → SSH and GPG keys → New SSH key"
echo ""
cat "${KEY_PATH}.pub"
echo ""
read -rp "Press ENTER once you have added the key to GitHub..." < /dev/tty

# ── 2. Test GitHub auth ─────────────────────────────────────────────────────
echo "==> Testing GitHub SSH connection..."
# ssh -T exits 1 even on success (no shell provided); suppress before pipe
{ ssh -T git@github.com 2>&1 || true; } | grep -q "successfully authenticated" \
  || { echo "ERROR: SSH auth failed. Check the key was added to GitHub."; exit 1; }
echo "    Auth OK."

# ── 3. Clone repo ───────────────────────────────────────────────────────────
echo "==> Cloning repository..."
git config --global user.name "$GITHUB_USER"
git config --global user.email "${GITHUB_USER}@twilio.com"

if [[ ! -d "$REPO_DIR/.git" ]]; then
  git clone "$REPO_URL" "$REPO_DIR"
else
  echo "    Repo already cloned at $REPO_DIR — skipping."
fi

# ── 4. Create personal auto-sync branch ────────────────────────────────────
echo "==> Setting up personal branch: $BRANCH"
cd "$REPO_DIR"
if git ls-remote --exit-code --heads origin "$BRANCH" > /dev/null 2>&1; then
  git checkout "$BRANCH"
  git pull origin "$BRANCH"
else
  git checkout -b "$BRANCH"
  git push -u origin "$BRANCH"
fi

# ── 5. Install JupyterLab post-save hook ───────────────────────────────────
echo "==> Installing JupyterLab post-save hook..."
mkdir -p "$HOME/.jupyter"
JUPYTER_CONFIG="$HOME/.jupyter/jupyter_server_config.py"

# Only add the hook block once
if ! grep -q "risk_analytics_auto_sync" "$JUPYTER_CONFIG" 2>/dev/null; then
  cat >> "$JUPYTER_CONFIG" <<'PYEOF'

# risk_analytics_auto_sync — auto-commit and push on every notebook save
import subprocess, os

def _auto_sync_on_save(os_path, model, **kwargs):
    repo_dir = os.path.expanduser("~/risk-analytics")
    if not os_path.startswith(repo_dir + os.sep):
        return  # only sync files inside the cloned repo (os.sep prevents prefix false-positives)
    try:
        subprocess.run(["git", "add", os_path], cwd=repo_dir, check=True, capture_output=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo_dir, capture_output=True
        )
        if result.returncode != 0:  # there are staged changes
            subprocess.run(
                ["git", "commit", "-m", f"auto: save {os.path.basename(os_path)}"],
                cwd=repo_dir, check=True, capture_output=True
            )
            subprocess.run(["git", "push"], cwd=repo_dir, check=True, capture_output=True)
    except Exception:
        pass  # never block a save due to any git or filesystem error

c.ContentsManager.post_save_hook = _auto_sync_on_save
PYEOF
fi

echo ""
echo "==> Setup complete."
echo "    Repo:   $REPO_DIR"
echo "    Branch: $BRANCH"
echo ""
echo "    From now on, every notebook save inside $REPO_DIR"
echo "    is automatically committed and pushed to GitHub."
echo ""
echo "    IMPORTANT: Restart your JupyterLab kernel server for the hook to take effect:"
echo "    In SageMaker Studio → File → Shut Down → restart your space."
