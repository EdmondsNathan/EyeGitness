use std::{path::Path, process::Command};

use crate::app::git::GitError;

pub(super) fn run_git(repo_path: &Path, args: &[&str]) -> Result<String, GitError> {
    let output = Command::new("git")
        .arg("-C")
        .arg(repo_path)
        .args(args)
        .output()?;

    if !output.status.success() {
        return Err(GitError::Git(
            String::from_utf8_lossy(&output.stderr).into_owned(),
        ));
    }

    Ok(String::from_utf8_lossy(&output.stdout).into_owned())
}

// TODO tests
