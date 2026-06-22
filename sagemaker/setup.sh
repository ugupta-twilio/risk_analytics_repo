#!/usr/bin/env bash
# One-time setup: SSH key, repo clone, and JupyterLab post-save hook for
# automatic git push to a ticket feature branch on every notebook save.
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

# ── 4. Install JupyterLab post-save hook (ticket-branch mode) ──────────────
echo "==> Installing JupyterLab post-save hook..."
mkdir -p "$HOME/.jupyter"
JUPYTER_CONFIG="$HOME/.jupyter/jupyter_server_config.py"

# Only add the hook block once
if ! grep -q "_is_sagemaker_path" "$JUPYTER_CONFIG" 2>/dev/null; then
  cat >> "$JUPYTER_CONFIG" <<'PYEOF'

# risk_analytics_auto_sync — auto-commit and push on every save (ticket-branch mode)
import subprocess, os
from pathlib import Path

_LOG = os.path.expanduser("~/.jupyter/sync-errors.log")

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
    # parts[-2] == 'sagemaker' ensures the file is directly inside sagemaker/ (not nested).
    # index >= 4 ensures there is at least one username component before sagemaker/.
    return (
        parts[0] == "projects"
        and parts[-2] == "sagemaker"
        and list(parts).index("sagemaker") >= 4
    )

def _find_repo_dir(os_path):
    """Return the git repo root containing os_path, or None if not inside a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=os.path.dirname(os.path.abspath(os_path)),
            capture_output=True, text=True
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None

def _find_sync_branch(os_path, repo_dir):
    """Walk up from os_path to find the nearest .sync-branch file inside the repo."""
    path = os.path.dirname(os.path.abspath(os_path))
    while path.startswith(repo_dir) and path != repo_dir:
        candidate = os.path.join(path, ".sync-branch")
        if os.path.isfile(candidate):
            branch = open(candidate).read().strip()
            return branch if branch else None
        path = os.path.dirname(path)
    return None

def _ensure_branch(repo_dir, branch):
    """Create branch from main if it doesn't exist remotely, then check it out."""
    result = subprocess.run(
        ["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
        cwd=repo_dir, capture_output=True
    )
    if result.returncode != 0:
        # Branch doesn't exist — create from main
        subprocess.run(["git", "fetch", "origin", "main"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-b", branch, "origin/main"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "push", "-u", "origin", branch], cwd=repo_dir, check=True, capture_output=True)
    else:
        # Branch exists — check it out if not already on it
        current = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_dir, capture_output=True, text=True
        ).stdout.strip()
        if current != branch:
            subprocess.run(["git", "checkout", branch], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "pull", "origin", branch], cwd=repo_dir, check=True, capture_output=True)

def _auto_sync_on_save(os_path, model, **kwargs):
    repo_dir = _find_repo_dir(os_path)
    if not repo_dir:
        return  # not inside a git repo — skip silently
    try:
        if _is_sagemaker_path(os_path, repo_dir):
            # Direct-to-main path for .ipynb files in <username>/sagemaker/
            subprocess.run(["git", "checkout", "main"], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "add", os_path], cwd=repo_dir, check=True, capture_output=True)
            diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_dir, capture_output=True)
            if diff.returncode != 0:
                subprocess.run(
                    ["git", "commit", "-m", f"auto: save {os.path.basename(os_path)}"],
                    cwd=repo_dir, check=True, capture_output=True
                )
                subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, check=True, capture_output=True)
        else:
            branch = _find_sync_branch(os_path, repo_dir)
            if not branch:
                return  # no .sync-branch file found — skip silently
            _ensure_branch(repo_dir, branch)
            subprocess.run(["git", "add", os_path], cwd=repo_dir, check=True, capture_output=True)
            diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_dir, capture_output=True)
            if diff.returncode != 0:
                subprocess.run(
                    ["git", "commit", "-m", f"auto: save {os.path.basename(os_path)}"],
                    cwd=repo_dir, check=True, capture_output=True
                )
                subprocess.run(["git", "push"], cwd=repo_dir, check=True, capture_output=True)
    except Exception as e:
        try:
            subprocess.run(["git", "rebase", "--abort"], cwd=repo_dir, capture_output=True)
        except Exception:
            pass
        with open(_LOG, "a") as f:
            f.write(f"{os_path}: {e}\n")

c.ContentsManager.post_save_hook = _auto_sync_on_save
PYEOF
fi

echo ""
echo "==> Setup complete."
echo "    Repo: $REPO_DIR"
echo ""
echo "    To enable auto-sync for a ticket:"
echo "    1. Create your folder: projects/<area>/<TICKET-ID>/$GITHUB_USER/"
echo "    2. Add a .sync-branch file with the target branch, e.g.:"
echo "       echo 'feature/RISK-3016' > projects/GM/RISK-3016/$GITHUB_USER/.sync-branch"
echo "    3. Restart your Studio space (File → Shut Down → restart)"
echo "    From then on, every save inside that folder auto-pushes to the branch."
