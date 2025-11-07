"""Small helper to run commands under the user's zsh environment safely.

This module provides a single function `run_zsh_command` that runs a
command via `zsh -c` after sourcing `~/.zshrc` (non-interactively). It
redirects stdin from DEVNULL so the child can't steal the TTY, supports a
timeout, and propagates common subprocess exceptions so callers can handle
them appropriately.

Usage:
    from zsh_runner import run_zsh_command
    cp = run_zsh_command("scp-sit /path/to/file", cwd="~/work/shacom-backend")
    print(cp.stdout)
"""
from __future__ import annotations

import shlex
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def run_zsh_command(
    cmd: str | list[str],
    cwd: Optional[str] = None,
    timeout: int = 30,
    capture_output: bool = True,
    check: bool = False,
    dry: bool = False,
) -> Optional[subprocess.CompletedProcess]:
    """Run `cmd` under zsh after sourcing the user's ~/.zshrc.

    Args:
        cmd: command string (or list of args) to run inside zsh -c
        cwd: working directory for subprocess
        timeout: seconds before raising subprocess.TimeoutExpired
        capture_output: whether to capture stdout/stderr
        check: whether to raise CalledProcessError on non-zero exit
        dry: if True, don't execute; just log and return None

    Returns:
        subprocess.CompletedProcess on success, or None if dry-run.

    Raises:
        FileNotFoundError: if zsh is not available
        subprocess.TimeoutExpired: if the process times out
        subprocess.CalledProcessError: if check is True and the process exits non-zero
        KeyboardInterrupt: if the caller interrupts the process
    """
    if dry:
        logger.info("DRY RUN - would run under zsh: %s (cwd=%s)", cmd, cwd)
        return None

    if isinstance(cmd, (list, tuple)):
        cmd = shlex.join(cmd)

    # Source the user's zsh config non-interactively, then run the command.
    # Redirect the sourcing output to /dev/null so ephemeral prints don't
    # pollute stdout.
    full_cmd = f"source ~/.zshrc >/dev/null 2>&1; {cmd}"
    args = ["zsh", "-c", full_cmd]

    try:
        cp = subprocess.run(
            args,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            check=check,
        )
        return cp
    except KeyboardInterrupt:
        logger.info("Interrupted while running zsh command: %s", cmd)
        raise
    except subprocess.TimeoutExpired:
        logger.error("zsh command timed out after %ss: %s", timeout, cmd)
        raise
    except FileNotFoundError:
        logger.error("zsh executable not found in PATH")
        raise
