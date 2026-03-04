import subprocess


def get_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_head_short() -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%h %s"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_ahead_behind() -> tuple[int, int]:
    result = subprocess.run(
        ["git", "rev-list", "--left-right", "--count", "@{upstream}...HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return (0, 0)
    parts = result.stdout.strip().split()
    if len(parts) == 2:
        return (int(parts[1]), int(parts[0]))
    return (0, 0)


def list_modified() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
    )
    return [f for f in result.stdout.splitlines() if f]


def list_staged() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )
    return [f for f in result.stdout.splitlines() if f]


def list_untracked() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
    )
    return [f for f in result.stdout.splitlines() if f]


def list_unmodified() -> list[str]:
    all_tracked = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    modified = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    changed = set(modified) | set(staged)
    return [f for f in all_tracked if f not in changed]
