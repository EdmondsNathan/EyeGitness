import subprocess
# watch -n1 --color -t "git diff --stat --color"
def stat_unstaged() -> str:
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
