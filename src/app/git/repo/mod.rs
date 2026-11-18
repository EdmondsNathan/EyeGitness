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

#[cfg(test)]
pub(super) mod test_utils {
    use super::*;
    use std::process::Command;

    /// Run a setup command in `dir` with the user's config isolated.
    pub(crate) fn git(dir: &Path, args: &[&str]) {
        let out = Command::new("git")
            .arg("-C")
            .arg(dir)
            .args(args)
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .env("GIT_TERMINAL_PROMPT", "0")
            .output()
            .expect("failed to launch git");
        assert!(
            out.status.success(),
            "git {args:?} failed: {}",
            String::from_utf8_lossy(&out.stderr)
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::process::Command;

    /// Run a setup command in `dir` with the user's config isolated.
    fn git(dir: &Path, args: &[&str]) {
        let out = Command::new("git")
            .arg("-C")
            .arg(dir)
            .args(args)
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .env("GIT_TERMINAL_PROMPT", "0")
            .output()
            .expect("failed to launch git");
        assert!(
            out.status.success(),
            "git {args:?} failed: {}",
            String::from_utf8_lossy(&out.stderr)
        );
    }

    /// Compare paths after resolving symlinks (macOS temp dirs live under
    /// /var, which is a symlink to /private/var).
    fn same_dir(a: &Path, b: &Path) -> bool {
        fs::canonicalize(a).unwrap() == fs::canonicalize(b).unwrap()
    }

    #[test]
    fn open_at_repo_root_returns_root() {
        let dir = tempfile::tempdir().unwrap();
        git(dir.path(), &["init", "-q"]);

        let repo = Repo::open(dir.path()).unwrap();
        assert!(same_dir(&repo.path, dir.path()));
    }

    #[test]
    fn open_from_subdirectory_resolves_to_root() {
        let dir = tempfile::tempdir().unwrap();
        git(dir.path(), &["init", "-q"]);
        let nested = dir.path().join("src").join("deep");
        fs::create_dir_all(&nested).unwrap();

        let repo = Repo::open(&nested).unwrap();
        assert!(same_dir(&repo.path, dir.path()));
    }

    #[test]
    fn open_outside_a_repo_is_an_error() {
        let dir = tempfile::tempdir().unwrap(); // no `git init`

        let result = Repo::open(dir.path());
        assert!(matches!(result, Err(GitError::Git(_))));
    }

    #[test]
    fn open_nonexistent_path_is_an_error() {
        let dir = tempfile::tempdir().unwrap();
        let missing = dir.path().join("does-not-exist");

        assert!(Repo::open(&missing).is_err());
    }

    #[test]
    fn open_bare_repo_is_an_error() {
        // --show-toplevel fails in a bare repo (no work tree), which is the
        // behavior we want for a staging tool.
        let dir = tempfile::tempdir().unwrap();
        git(dir.path(), &["init", "-q", "--bare"]);

        assert!(Repo::open(dir.path()).is_err());
    }

    #[test]
    fn open_path_with_spaces() {
        let base = tempfile::tempdir().unwrap();
        let spaced = base.path().join("my repo");
        fs::create_dir(&spaced).unwrap();
        git(&spaced, &["init", "-q"]);

        let repo = Repo::open(&spaced).unwrap();
        assert!(same_dir(&repo.path, &spaced));
    }

    #[test]
    fn open_inside_dot_git_directory_is_an_error() {
        // Inside .git there's no work tree, so --show-toplevel fails.
        let dir = tempfile::tempdir().unwrap();
        git(dir.path(), &["init", "-q"]);

        assert!(Repo::open(&dir.path().join(".git")).is_err());
    }

    #[test]
    fn open_result_has_no_trailing_newline() {
        let dir = tempfile::tempdir().unwrap();
        git(dir.path(), &["init", "-q"]);

        let repo = Repo::open(dir.path()).unwrap();
        let s = repo.path.to_string_lossy();
        assert!(!s.ends_with('\n') && !s.ends_with('\r'));
    }

    #[test]
    fn open_nested_repo_resolves_to_innermost() {
        // A repo inside another repo's directory: the inner one wins.
        let outer = tempfile::tempdir().unwrap();
        git(outer.path(), &["init", "-q"]);
        let inner = outer.path().join("vendor").join("lib");
        fs::create_dir_all(&inner).unwrap();
        git(&inner, &["init", "-q"]);

        let repo = Repo::open(&inner).unwrap();
        assert!(same_dir(&repo.path, &inner));
    }
}
