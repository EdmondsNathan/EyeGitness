pub(super) use api::{diff_file, status, DiffMode};
pub(super) use git_error::GitError;
pub(crate) use git_file::{ConflictKind, FileState, FileStatus, GitFile};

mod api;
mod git_error;
mod git_file;
mod parse;
mod runner;
