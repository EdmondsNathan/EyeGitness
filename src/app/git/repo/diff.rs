use crate::app::{
    git::{parse, runner, GitError, Repo},
    GitFile,
};

pub(crate) struct Diff {
    // TODO
}

pub(crate) enum DiffMode {
    Staged,
    Unstaged,
}

impl Repo {
    // TODO Implement a Diff type to allow better parsing of Diffs
    pub(crate) fn diff(&self, file: GitFile, mode: DiffMode) -> Result<Option<Diff>, GitError> {
        let mut args = vec!["diff", "--no-color"];

        if let DiffMode::Staged = mode {
            args.push("--cached");
        }

        args.extend(["--", &file.path]);

        parse::diff(&runner::run_git(&self.path, &args)?)
    }
}

// TODO tests
