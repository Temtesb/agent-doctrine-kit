# Background-process ↔ user-commit git-lock coordination

## The pattern

Any project with a background process touching git will eventually orphan a `.git/index.lock`. The user attempts a commit; git fails with *"Unable to create '.git/index.lock'"*. The actual holder of the lock is long-dead — a background process that crashed mid-operation, or whose process tree was killed without releasing.

The fix is a context-manager wrapper that any background process must use when invoking git, with three properties: explicit acquire/release semantics, a watchdog that frees orphaned locks (where the named PID is no longer running), and a user-priority sentinel file the user can drop to tell background loops to back off.

**Anchored to:** Foundation [F1](../01_foundations/F1_time_has_direction.md) — lock-acquire and lock-release are paired temporal events; an orphaned lock erases the release half of the historical record, so any future observer cannot tell whether the lock is held by a live process or is dead infrastructure. Also [F3](../01_foundations/F3_information_asymmetric_durability.md) — the held-state of a lock outlives the durability of the process that held it, which is exactly the asymmetric-durability failure F3 names. The lock's state outlasts its holder; without an explicit lifetime contract, the state is unverifiable.

## Seed evidence

Two concrete instances in a single 24-hour window, in two different projects:

1. **Project A** — user's `git commit` at ~06:33 local hit `fatal: Unable to create '.git/index.lock'`. The lock had been orphaned by an earlier background run; `ps aux | grep git` confirmed no live holder. Cleared manually with `rm .git/index.lock`.

2. **Project B** — same shape, ~6 hours later. User's `git commit` at ~12:40 local hit the same error. The background run-loop had kicked off at 16:33:00Z (12:33 EDT) — and the cowork-run lock recorded "force-rotated 720-min stale lock" on startup, meaning the lock-rotation problem existed *one level up too* (the cowork-lock itself accumulates 12-hour-stale instances). The git operation the loop ran left `.git/index.lock` orphaned 7 minutes later. Cleared manually.

Two instances in two different repos, same shape, same root cause, six hours apart. The loop-startup framing (*"force-rotated 720-min stale lock"*) confirms the same failure mode propagates up the lock-hierarchy: every layer needs explicit acquire/release with a watchdog or the orphan accumulates.

## The fix shape

A `cowork_git_quiesce()` wrapper that any background process MUST use when invoking git:

```python
from contextlib import contextmanager

@contextmanager
def cowork_git_quiesce(repo_path: Path, operation: str):
    """Background processes touching git use this. Explicit acquire/release;
    sentinel-file check before acquiring; watchdog cleans up orphans."""
    sentinel = repo_path / ".cowork-quiesce"
    if sentinel.exists():
        # User has signaled they're about to commit. Defer.
        logger.info(f"cowork_git_quiesce: sentinel present; deferring {operation}")
        yield None  # caller checks for None and skips
        return

    lock_file = repo_path / ".cowork_git.lock"
    try:
        _acquire_lock(lock_file, operation=operation)
        yield True
    finally:
        _release_lock(lock_file)
        # Best-effort cleanup: if git crashed mid-op, .git/index.lock
        # may exist. Check for orphan and clean up.
        _cleanup_orphaned_git_index_lock(repo_path)


def _acquire_lock(lock_file: Path, operation: str, timeout: int = 30):
    """Write sidecar file recording PID, start time, operation type."""
    import os
    import time
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with open(lock_file, "x") as f:
                f.write(f"pid={os.getpid()}\n")
                f.write(f"acquired_at={datetime.now().isoformat()}\n")
                f.write(f"operation={operation}\n")
            return
        except FileExistsError:
            if _lock_is_orphaned(lock_file):
                # Watchdog: the PID in the lock file is no longer running.
                # Force-rotate.
                lock_file.rename(lock_file.with_suffix(f".stale.{int(time.time())}"))
                continue
            time.sleep(0.5)
    raise LockHeldError(f"Could not acquire {lock_file} within {timeout}s")


def _lock_is_orphaned(lock_file: Path) -> bool:
    """Check if the PID named in the lock file is no longer running."""
    import os
    import re
    try:
        contents = lock_file.read_text()
        pid_match = re.search(r"pid=(\d+)", contents)
        if not pid_match:
            return True  # malformed; treat as orphan
        pid = int(pid_match.group(1))
        try:
            os.kill(pid, 0)  # signal 0 = check existence
            return False     # process is alive
        except ProcessLookupError:
            return True
    except OSError:
        return True


def _release_lock(lock_file: Path):
    """Append RELEASED marker; remove lock file."""
    try:
        with open(lock_file, "a") as f:
            f.write(f"RELEASED={datetime.now().isoformat()}\n")
        lock_file.unlink(missing_ok=True)
    except OSError:
        pass  # best-effort


def _cleanup_orphaned_git_index_lock(repo_path: Path):
    """If git's .git/index.lock exists and no git process is running,
    clean it up. Best-effort; the watchdog above is the primary
    mechanism."""
    git_index_lock = repo_path / ".git" / "index.lock"
    if git_index_lock.exists():
        # Only safe to remove if no git process is running.
        if not _any_git_process_running():
            git_index_lock.unlink(missing_ok=True)


def _any_git_process_running() -> bool:
    """Best-effort check for live git processes."""
    import subprocess
    try:
        result = subprocess.run(
            ["pgrep", "-f", "git"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
```

## How the user-priority sentinel works

The `.cowork-quiesce` sentinel file is a small inversion-of-control mechanism. When the user is about to commit and wants background processes to back off, they drop the sentinel:

```bash
touch .cowork-quiesce
# do work, commit, etc.
rm .cowork-quiesce
```

The background process's wrapper checks for the sentinel before acquiring the lock. If present, the wrapper returns `None` to the caller, and the caller skips the git operation (logging the deferral). The user is the priority signal; background work yields.

Optional escalation: hourly windows that the background loop voluntarily yields without needing a sentinel (e.g., 09:00-18:00 weekday local time when the user is likely active).

## Why this belongs at the stack layer

Any project bootstrapped from a stack that grows a background process touching git (autonomous run-loop, scheduled CI, integrity sweeps, automated commits) will have the same lock-coordination problem. The shape is fully determined by *"background process + user-driven commits share a git working tree,"* not by what the project does.

Filing the wrapper at the stack layer means every project that adopts the stack inherits it.

## Adopt this in your project

1. Copy the wrapper code into your project (`foundation/git_coordination.py` or similar).
2. Audit every background-process call to `git` and wrap it in `cowork_git_quiesce`.
3. Document the sentinel file convention in your project's user-facing docs.
4. Optional: add a watchdog cron that runs `_cleanup_orphaned_git_index_lock` every minute as a defense in depth.

## Elevation status

**Currently staged.** All four elevation criteria are close to passing:

- ✓ Generative force — explains rules about lock-state lifetime, asymmetric durability, lock-hierarchy propagation
- ✓ Reduction-resistance — derives from F1 + F3 but not from existing stack-layer rules
- ✓ Falsifiability — would be falsified by a system where lock-state asymmetric durability isn't a failure mode (none observed)
- ✓ Independent triangulation — two project sightings in two different repos, same root cause, surfaced 6 hours apart

Cross-project independence is moderate (same author, same AI). A third sighting in a project with different authorship would advance the evidence to clear elevation.
