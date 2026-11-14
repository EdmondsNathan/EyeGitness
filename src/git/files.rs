use std::process::Command;

pub(crate) fn untracked_files() -> std::result::Result<Vec<String>, std::io::Error> {
    let output = Command::new("git")
        .args(["ls-files", "--others", "--exclude-standard"])
        .output()?;
    Ok(String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(String::from)
        .collect())
}

pub(crate) fn modified_files() -> std::result::Result<Vec<String>, std::io::Error> {
    let output = Command::new("git").args(["diff", "--name-only"]).output()?;
    Ok(String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(String::from)
        .collect())
}
