use crate::app::{
    GitFile,
    git::{GitError, Repo, parse, runner},
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
        // TODO check that file can be diffed(not untracked or other edge cases)

        let mut args = vec!["diff", "--no-color"];

        if let DiffMode::Staged = mode {
            args.push("--cached");
        }

        args.extend(["--", &file.path]);

        parse::diff(&runner::run_git(&self.path, &args)?)
    }
}

// TODO tests
