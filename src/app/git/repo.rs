use std::path::{Path, PathBuf};

use crate::app::git::{parse, runner, FileStatus, GitError, GitFile};

pub(crate) struct Repo {
    path: PathBuf,
}

pub(crate) enum DiffMode {
    Staged,
    Unstaged,
}

impl Repo {
    pub(crate) fn open(path: &Path) -> Result<Repo, GitError> {
        let output = runner::run_git(path, &["rev-parse", "--show-top-level"])?;
        let root = PathBuf::from(output.trim_end_matches(['\n', '\r']));
        Ok(Repo { path: root })
    }

    pub(crate) fn diff(&self) -> Result<String, GitError> {
        runner::run_git(&self.path, &["diff", "--no-color"])
    }

    // TODO Implement a Diff type to allow better parsing of Diffs
    pub(crate) fn diff_file(&self, file: GitFile, mode: DiffMode) -> Result<String, GitError> {
        let mut args = vec!["diff", "--no-color"];

        if let DiffMode::Staged = mode {
            args.push("--cached");
        }

        args.extend(["--", &file.path]);

        runner::run_git(&self.path, &args)
    }

    pub(crate) fn status(&self) -> Result<Vec<GitFile>, GitError> {
        parse::status(&runner::run_git(
            &self.path,
            &["status", "--porcelain", "-z"],
        )?)
    }
}
