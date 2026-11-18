use crate::app::git::{runner, GitError};
use std::path::{Path, PathBuf};

pub(crate) use diff::DiffMode;

mod diff;
mod status;

pub(crate) struct Repo {
    path: PathBuf,
}

impl Repo {
    pub(crate) fn open(path: &Path) -> Result<Repo, GitError> {
        let output = runner::run_git(path, &["rev-parse", "--show-toplevel"])?;
        let root = PathBuf::from(output.trim_end_matches(['\n', '\r']));
        Ok(Repo { path: root })
    }
}
