#![allow(unused)]
mod git;

pub(crate) use git::{ConflictKind, FileState, FileStatus, GitFile, Repo};
