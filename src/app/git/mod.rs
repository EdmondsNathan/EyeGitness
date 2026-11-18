pub(super) use git_error::GitError;
pub(crate) use git_file::{ConflictKind, FileState, FileStatus, GitFile};
pub(super) use repo::{DiffMode, Repo};

mod git_error;
mod git_file;
mod parse;
mod repo;
mod runner;
