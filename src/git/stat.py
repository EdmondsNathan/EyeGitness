import subprocess


def stat_modified() -> str:
    stat = subprocess.run([
        "git",
        "diff",
        "--stat",
        "--color",
        ],
        capture_output=True,
        text=True
      ).stdout

    return stat


def stat_untracked() -> str:
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
    )
    return result.stdout


def stat_staged() -> str:
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat", "--color"],
        capture_output=True,
        text=True,
    )
    return result.stdout


def stat_unmodified() -> str:
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
    unmodified = [f for f in all_tracked if f not in changed]
    return "\n".join(unmodified) + "\n" if unmodified else ""
