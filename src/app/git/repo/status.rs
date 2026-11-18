use crate::app::{
    git::{parse, runner, GitError, Repo},
    GitFile,
};

impl Repo {
    pub(crate) fn status(&self) -> Result<Vec<GitFile>, GitError> {
        parse::status(&runner::run_git(
            &self.path,
            &["status", "--porcelain", "-z"],
        )?)
    }
}

//TODO tests
