import subprocess

def diff_unstaged() -> str:
    diff = subprocess.Popen([
        "git",
        "diff",
        ],
        stdout=subprocess.PIPE
    )

    grep = subprocess.run([
        "grep", 
        "-e",
        r"^-\+",
        "-e",
        r"^\+\+",
        ],
        stdin=diff.stdout,
        capture_output=True,
        text=True
    ).stdout

    return grep
