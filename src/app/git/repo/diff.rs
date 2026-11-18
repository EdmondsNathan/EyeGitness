use crate::app::{
    git::{runner, GitError, Repo},
    GitFile,
};

pub(crate) enum DiffMode {
    Staged,
    Unstaged,
}

impl Repo {
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
}
