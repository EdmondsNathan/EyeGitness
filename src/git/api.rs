use crate::git::{runner, GitError};

pub(crate) fn diff() -> Result<String, GitError> {
    runner::run_git(&["diff", "--no-color"])
}

pub(crate) fn diff_file(file_name: &str) -> Result<String, GitError> {
    runner::run_git(&["diff", "--no-color", "--", file_name])
}

pub(crate) fn untracked_files() -> Result<Vec<String>, GitError> {
    Ok(
        runner::run_git(&["ls-files", "-z", "--others", "--exclude-standard"])?
            .split('\0')
            .map(String::from)
            .collect(),
    )
}

pub(crate) fn modified_files() -> Result<Vec<String>, GitError> {
    Ok(runner::run_git(&["diff", "--name-only", "-z"])?
        .split('\0')
        .map(String::from)
        .collect())
}
