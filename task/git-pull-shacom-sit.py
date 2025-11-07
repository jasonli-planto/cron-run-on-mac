## this python script defines the logic of the task
## it will be run im case of the task id is returned by the cron-event script

import logging
from datetime import datetime
import os
import subprocess
import shlex
import glob
from typing import Optional
from zsh_runner import run_zsh_command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
    """Perform these steps:

    - Ensure repo at ~/work/shacom-backend exists
    - Fetch and update local `sit` branch from `origin/sit`
    - Run build script: ./build-scripts/build-container-only.sh iads
    - Run `apptest` in an interactive zsh to pick up user's zsh functions/aliases
    - Find the most recent file matching `be-iads-*.tar.gz` (recursive in repo_dir)
    - Run `scp-sit <path>` in an interactive zsh so any shell function/alias is available

    Safety: if environment variable DRY_RUN is set to a truthy value ("1","true"),
    commands that make external side-effects will be logged but not executed.

    Returns True on success, False on any failure.
    """

    logger.info("Running task: git-pull-shacom-sit")
    repo_dir = os.path.expanduser("~/work/shacom-backend")
    dry = os.environ.get("DRY_RUN", os.environ.get("CRON_RUN_DRY", "")).lower() in ("1", "true", "yes")

    if not os.path.isdir(repo_dir):
        logger.error("Repository directory does not exist: %s", repo_dir)
        return False

    def run_cmd(cmd, cwd: Optional[str] = None, use_zsh=False, check=True):
        """Run a command and return subprocess.CompletedProcess or None if dry-run."""
        if dry:
            logger.info("DRY RUN - would run: %s (cwd=%s)", cmd, cwd)
            return None

        if isinstance(cmd, str):
            args = cmd if use_zsh else shlex.split(cmd)
        else:
            args = cmd

        logger.info("Running command: %s (cwd=%s)", cmd, cwd)
        try:
            if use_zsh:
                # run under interactive zsh to pick up user functions/aliases
                # Use the centralized, non-interactive runner which sources
                # the user's zsh config but avoids spawning an interactive
                # shell that can grab the TTY.
                completed = run_zsh_command(cmd, cwd=cwd, timeout=120, check=check)
                # run_zsh_command returns CompletedProcess when not dry-run
                if completed is None:
                    return None
            else:
                completed = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=check)
            logger.debug("stdout: %s", completed.stdout)
            logger.debug("stderr: %s", completed.stderr)
            return completed
        except subprocess.CalledProcessError as e:
            logger.error("Command failed (%s): %s", e.returncode, e)
            logger.error("stdout: %s", getattr(e, 'stdout', None))
            logger.error("stderr: %s", getattr(e, 'stderr', None))
            raise

    try:
        # 1) fetch and update sit branch
        run_cmd("git fetch origin sit", cwd=repo_dir)
        run_cmd("git checkout sit", cwd=repo_dir)
        run_cmd("git pull origin sit", cwd=repo_dir)

        # 2) run build script
        build_script = os.path.join(repo_dir, "build-scripts", "build-container-only.sh")
        if not os.path.exists(build_script):
            logger.error("Build script not found: %s", build_script)
            return False
        # ensure executable (best-effort)
        try:
            os.chmod(build_script, os.stat(build_script).st_mode | 0o111)
        except Exception:
            logger.debug("Could not set executable bit on build script (continuing)")

        # run_cmd(f"{shlex.quote(build_script)} iads", cwd=repo_dir)

        # 3) run apptest in interactive zsh to switch wifi
        # Run as zsh -i -c 'apptest' so user's ~/.zshrc is sourced
        run_cmd("apptest", use_zsh=True)

        # 4) find latest be-iads-*.tar.gz in repo_dir (search recursive)
        pattern = os.path.join(repo_dir, "**", "be-iads-*.tar.gz")
        matches = glob.glob(pattern, recursive=True)
        if not matches:
            logger.error("No matching build image files found with pattern %s", pattern)
            return False

        latest = max(matches, key=lambda p: os.path.getmtime(p))
        logger.info("Found latest image: %s", latest)

        # 5) run scp-sit via interactive zsh to pick user's script/alias
        cmd = f"scp-sit {shlex.quote(latest)}"
        # run_cmd(cmd, use_zsh=True)

        logger.info("Task completed successfully at %s", datetime.utcnow().isoformat() + "Z")
        return True

    except Exception as exc:
        logger.exception("Task failed: %s", exc)
        return False