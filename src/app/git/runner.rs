use std::{path::Path, process::Command};

use crate::app::git::GitError;

pub(super) fn run_git(repo_path: &Path, args: &[&str]) -> Result<String, GitError> {
    let output = Command::new("git")
        .arg("-C")
        .arg(repo_path)
        .args(args)
        .output()?;

    if !output.status.success() {
        return Err(GitError::Git(
            String::from_utf8_lossy(&output.stderr).into_owned(),
        ));
    }

    Ok(String::from_utf8_lossy(&output.stdout).into_owned())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::app::git::repo::test_utils::git;
    use std::fs;

    #[test]
    fn returns_stdout_on_success() {
        let dir = tempfile::tempdir().unwrap();
        git(dir.path(), &["init", "-q"]);

        let out = run_git(dir.path(), &["rev-parse", "--is-inside-work-tree"]).unwrap();
        assert_eq!(out.trim(), "true");
    }

    #[test]
    fn runs_in_the_given_directory() {
        // Two repos, each with a different file. Each call must see only its own.
        let a = tempfile::tempdir().unwrap();
        let b = tempfile::tempdir().unwrap();
        git(a.path(), &["init", "-q"]);
        git(b.path(), &["init", "-q"]);
        fs::write(a.path().join("only_in_a.txt"), "x").unwrap();
        fs::write(b.path().join("only_in_b.txt"), "y").unwrap();

        let out_a = run_git(a.path(), &["ls-files", "--others", "--exclude-standard"]).unwrap();
        let out_b = run_git(b.path(), &["ls-files", "--others", "--exclude-standard"]).unwrap();

        assert!(out_a.contains("only_in_a.txt"));
        assert!(!out_a.contains("only_in_b.txt"));
        assert!(out_b.contains("only_in_b.txt"));
    }

    #[test]
    fn empty_stdout_is_ok_not_error() {
        let dir = tempfile::tempdir().unwrap();
        git(dir.path(), &["init", "-q"]);

        let out = run_git(dir.path(), &["status", "--porcelain=v1", "-z"]).unwrap();
        assert!(out.is_empty());
    }

    #[test]
    fn outside_a_repo_is_a_git_error_with_stderr() {
        let dir = tempfile::tempdir().unwrap(); // plain directory, no `git init`

        match run_git(dir.path(), &["rev-parse", "--show-toplevel"]) {
            Err(GitError::Git(stderr)) => assert!(!stderr.is_empty()),
            other => panic!("expected GitError::Git, got {other:?}"),
        }
    }

    #[test]
    fn bad_subcommand_is_a_git_error() {
        let dir = tempfile::tempdir().unwrap();
        git(dir.path(), &["init", "-q"]);

        let result = run_git(dir.path(), &["not-a-real-subcommand"]);
        assert!(matches!(result, Err(GitError::Git(_))));
    }

    #[test]
    fn nonexistent_directory_is_an_error() {
        let dir = tempfile::tempdir().unwrap();
        let missing = dir.path().join("does-not-exist");

        // `git -C <missing>` fails with a nonzero exit, so this is GitError::Git,
        // not Io: git launched fine, it just couldn't change directory.
        let result = run_git(&missing, &["status"]);
        assert!(matches!(result, Err(GitError::Git(_))));
    }

    #[test]
    fn path_with_spaces_works() {
        let base = tempfile::tempdir().unwrap();
        let spaced = base.path().join("my repo");
        fs::create_dir(&spaced).unwrap();
        git(&spaced, &["init", "-q"]);

        let out = run_git(&spaced, &["rev-parse", "--is-inside-work-tree"]).unwrap();
        assert_eq!(out.trim(), "true");
    }

    #[test]
    fn argument_is_passed_as_one_arg_not_split_by_a_shell() {
        // A pathspec containing a space must reach git as a single argument.
        let dir = tempfile::tempdir().unwrap();
        git(dir.path(), &["init", "-q"]);
        fs::write(dir.path().join("a b.txt"), "x").unwrap();

        let out = run_git(
            dir.path(),
            &[
                "ls-files",
                "--others",
                "--exclude-standard",
                "--",
                "a b.txt",
            ],
        )
        .unwrap();
        assert!(out.contains("a b.txt"));
    }
}
