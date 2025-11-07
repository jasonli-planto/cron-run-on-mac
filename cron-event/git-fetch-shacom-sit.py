## this python script will be loaded by main.py at the time specified in cron.json
## this script should contains logic that decide whether to run the task or not and return the task id if it should be run
## task id is a string defined in task-definition.json

import os
import subprocess


def task_id():
    if should_run_task():
        return "git-pull-shacom-sit"
    return None


def should_run_task() -> bool:
    """
    Return True when remote branch origin/sit has commits not present in the local branch 'sit'.

    Workflow:
    - cd to ~/work/bfm-backend
    - git fetch origin sit
    - run `git rev-list --count sit..origin/sit` and return True if the count > 0

    Returns False on errors or when there are no new commits.
    """
    repo_dir = os.path.expanduser("~/work/shacom-backend")

    # Make sure repository directory exists
    if not os.path.isdir(repo_dir):
        print(f"Repository path does not exist: {repo_dir}")
        return False
    
    # switch to scb wifi first
    # "scb5g" is defined in the user's zsh configuration (e.g. ~/.zshrc).
    # Run it through an interactive zsh so that zshrc is sourced and the
    # function/alias is available.
    scbwifi_cmd = ["zsh", "-i", "-c", "scb5g"]
    try:
        proc = subprocess.run(scbwifi_cmd, cwd=repo_dir, capture_output=True, text=True)
    except FileNotFoundError:
        print("zsh executable not found in PATH")
        return False
    except Exception as e:
        print(f"Unexpected error switching wifi: {e}")
        return False

    if proc.returncode != 0:
        stderr = proc.stderr.strip() if proc.stderr else ""
        print(f"scb5g command failed (rc={proc.returncode}): {stderr}")
        return False

    # Fetch the remote branch
    fetch_cmd = ["git", "fetch", "origin", "sit"]
    try:
        proc = subprocess.run(fetch_cmd, cwd=repo_dir, capture_output=True, text=True)
    except FileNotFoundError:
        print("git executable not found in PATH")
        return False
    except Exception as e:
        print(f"Unexpected error running git fetch: {e}")
        return False

    if proc.returncode != 0:
        stderr = proc.stderr.strip() if proc.stderr else ""
        print(f"git fetch failed (rc={proc.returncode}): {stderr}")
        return False

    # Count commits that are in origin/sit but not in sit
    rev_cmd = ["git", "rev-list", "--count", "sit..origin/sit"]
    proc2 = subprocess.run(rev_cmd, cwd=repo_dir, capture_output=True, text=True)
    if proc2.returncode != 0:
        stderr = proc2.stderr.strip() if proc2.stderr else ""
        print(f"git rev-list failed (rc={proc2.returncode}): {stderr}")
        return False

    out = proc2.stdout.strip()
    try:
        count = int(out)
    except Exception:
        print(f"Unable to parse rev-list output: {out!r}")
        return False

    if count > 0:
        print(f"Detected {count} new commit(s) on origin/sit")
        return True

    # no new commits
    return False