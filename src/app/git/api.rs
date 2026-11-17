use crate::app::git::{FileStatus, GitError, GitFile, parse, runner};

pub(crate) fn diff() -> Result<String, GitError> {
    runner::run_git(&["diff", "--no-color"])
}

pub(crate) enum DiffMode {
    Staged,
    Unstaged,
}

// TODO Implement a Diff type to allow better parsing of Diffs
pub(crate) fn diff_file(file: GitFile, mode: DiffMode) -> Result<String, GitError> {
    let mut args = vec!["diff", "--no-color"];

    if let DiffMode::Staged = mode {
        args.push("--cached");
    }

    args.extend(["--", &file.path]);

    runner::run_git(&args)
}

pub(crate) fn status() -> Result<Vec<GitFile>, GitError> {
    parse::status(&runner::run_git(&["status", "--porcelain", "-z"])?)
}
