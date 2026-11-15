use std::process::Command;

use crate::git::GitError;

impl From<std::io::Error> for GitError {
    fn from(error: std::io::Error) -> Self {
        GitError::Io(error)
    }
}

pub(super) fn run_git(args: &[&str]) -> Result<String, GitError> {
    let output = Command::new("git").args(args).output()?;

    if !output.status.success() {
        return Err(GitError::Git(
            String::from_utf8_lossy(&output.stderr).into_owned(),
        ));
    }

    Ok(String::from_utf8_lossy(&output.stdout).into_owned())
}
