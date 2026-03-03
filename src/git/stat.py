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
