use crate::app::{
    git::{parse, runner, GitError, Repo},
    GitFile,
};

impl Repo {
    pub(crate) fn status(&self) -> Result<Vec<GitFile>, GitError> {
        parse::status(&runner::run_git(
            &self.path,
            &["status", "--porcelain", "-z", "--untracked-files=all"],
        )?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::app::git::repo::test_utils::{git, init_repo};
    use crate::app::{ConflictKind, FileState, FileStatus};
    use std::fs;

    fn normal(index: Option<FileStatus>, working_tree: Option<FileStatus>) -> FileState {
        FileState::Normal {
            index,
            working_tree,
        }
    }

    fn find<'a>(files: &'a [GitFile], path: &str) -> &'a GitFile {
        files
            .iter()
            .find(|f| f.path == path)
            .unwrap_or_else(|| panic!("{path} not in {files:?}"))
    }

    #[test]
    fn clean_repo_has_no_files() {
        let dir = init_repo();
        let repo = Repo::open(dir.path()).unwrap();

        assert!(repo.status().unwrap().is_empty());
    }

    #[test]
    fn empty_repo_without_commits_works() {
        let dir = tempfile::tempdir().unwrap();
        git(dir.path(), &["init", "-q"]);
        fs::write(dir.path().join("a.txt"), "x").unwrap();

        let repo = Repo::open(dir.path()).unwrap();
        let files = repo.status().unwrap();
        assert_eq!(find(&files, "a.txt").state, FileState::Untracked);
    }

    #[test]
    fn modified_unstaged() {
        let dir = init_repo();
        fs::write(dir.path().join("README.md"), "changed\n").unwrap();

        let repo = Repo::open(dir.path()).unwrap();
        let files = repo.status().unwrap();
        assert_eq!(
            find(&files, "README.md").state,
            normal(None, Some(FileStatus::Modified))
        );
    }

    #[test]
    fn staged_modification() {
        let dir = init_repo();
        fs::write(dir.path().join("README.md"), "changed\n").unwrap();
        git(dir.path(), &["add", "README.md"]);

        let repo = Repo::open(dir.path()).unwrap();
        let files = repo.status().unwrap();
        assert_eq!(
            find(&files, "README.md").state,
            normal(Some(FileStatus::Modified), None)
        );
    }

    #[test]
    fn staged_then_modified_again() {
        let dir = init_repo();
        let p = dir.path();
        fs::write(p.join("README.md"), "one\n").unwrap();
        git(p, &["add", "README.md"]);
        fs::write(p.join("README.md"), "two\n").unwrap();

        let repo = Repo::open(p).unwrap();
        let files = repo.status().unwrap();
        assert_eq!(
            find(&files, "README.md").state,
            normal(Some(FileStatus::Modified), Some(FileStatus::Modified))
        );
    }

    #[test]
    fn staged_new_file() {
        let dir = init_repo();
        fs::write(dir.path().join("new.txt"), "x").unwrap();
        git(dir.path(), &["add", "new.txt"]);

        let repo = Repo::open(dir.path()).unwrap();
        let files = repo.status().unwrap();
        assert_eq!(
            find(&files, "new.txt").state,
            normal(Some(FileStatus::Added), None)
        );
    }

    #[test]
    fn untracked_file_with_spaces() {
        let dir = init_repo();
        fs::write(dir.path().join("new file.txt"), "x").unwrap();

        let repo = Repo::open(dir.path()).unwrap();
        let files = repo.status().unwrap();
        assert_eq!(find(&files, "new file.txt").state, FileState::Untracked);
    }

    #[test]
    fn non_ascii_filename_is_not_quoted() {
        // Without -z git would emit "caf\303\251.txt" with quotes.
        let dir = init_repo();
        fs::write(dir.path().join("café.txt"), "x").unwrap();

        let repo = Repo::open(dir.path()).unwrap();
        let files = repo.status().unwrap();
        assert_eq!(find(&files, "café.txt").state, FileState::Untracked);
    }

    #[test]
    fn deleted_unstaged_and_staged() {
        let dir = init_repo();
        let p = dir.path();
        fs::write(p.join("a.txt"), "a").unwrap();
        fs::write(p.join("b.txt"), "b").unwrap();
        git(p, &["add", "."]);
        git(p, &["commit", "-q", "-m", "add files"]);

        fs::remove_file(p.join("a.txt")).unwrap(); // unstaged delete
        git(p, &["rm", "-q", "b.txt"]); // staged delete

        let repo = Repo::open(p).unwrap();
        let files = repo.status().unwrap();
        assert_eq!(
            find(&files, "a.txt").state,
            normal(None, Some(FileStatus::Deleted))
        );
        assert_eq!(
            find(&files, "b.txt").state,
            normal(Some(FileStatus::Deleted), None)
        );
    }

    #[test]
    fn rename_reports_orig_path() {
        let dir = init_repo();
        git(dir.path(), &["mv", "README.md", "DOCS.md"]);

        let repo = Repo::open(dir.path()).unwrap();
        let files = repo.status().unwrap();
        let f = find(&files, "DOCS.md");
        assert_eq!(f.state, normal(Some(FileStatus::Renamed), None));
        assert_eq!(f.orig_path.as_deref(), Some("README.md"));
    }

    #[test]
    fn record_after_rename_still_parses() {
        let dir = init_repo();
        let p = dir.path();
        git(p, &["mv", "README.md", "DOCS.md"]);
        fs::write(p.join("other.txt"), "x").unwrap();

        let repo = Repo::open(p).unwrap();
        let files = repo.status().unwrap();
        assert_eq!(files.len(), 2);
        assert_eq!(find(&files, "other.txt").state, FileState::Untracked);
    }

    #[test]
    fn type_change_file_to_symlink() {
        // Symlinks need privileges on Windows, so Unix only.
        #[cfg(unix)]
        {
            let dir = init_repo();
            let p = dir.path();
            fs::remove_file(p.join("README.md")).unwrap();
            std::os::unix::fs::symlink("/etc/hostname", p.join("README.md")).unwrap();

            let repo = Repo::open(p).unwrap();
            let files = repo.status().unwrap();
            assert_eq!(
                find(&files, "README.md").state,
                normal(None, Some(FileStatus::TypeChanged))
            );
        }
    }

    #[test]
    fn merge_conflict_is_both_modified() {
        let dir = init_repo();
        let p = dir.path();
        git(p, &["checkout", "-q", "-b", "feature"]);
        fs::write(p.join("README.md"), "feature\n").unwrap();
        git(p, &["commit", "-q", "-am", "feature change"]);
        git(p, &["checkout", "-q", "-"]);
        fs::write(p.join("README.md"), "main\n").unwrap();
        git(p, &["commit", "-q", "-am", "main change"]);

        // The merge is expected to fail with a conflict, so don't use the helper.
        let _ = std::process::Command::new("git")
            .arg("-C")
            .arg(p)
            .args(["merge", "feature"])
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .output()
            .unwrap();

        let repo = Repo::open(p).unwrap();
        let files = repo.status().unwrap();
        assert_eq!(
            find(&files, "README.md").state,
            FileState::Conflicted(ConflictKind::BothModified)
        );
    }

    #[test]
    fn untracked_files_in_new_directory_are_listed_individually() {
        // Needs --untracked-files=all; by default git collapses to "dir/".
        let dir = init_repo();
        let nested = dir.path().join("newdir");
        fs::create_dir(&nested).unwrap();
        fs::write(nested.join("a.txt"), "a").unwrap();
        fs::write(nested.join("b.txt"), "b").unwrap();

        let repo = Repo::open(dir.path()).unwrap();
        let files = repo.status().unwrap();
        assert!(files.iter().any(|f| f.path == "newdir/a.txt"));
        assert!(files.iter().any(|f| f.path == "newdir/b.txt"));
    }

    #[test]
    fn gitignored_files_are_not_listed() {
        let dir = init_repo();
        let p = dir.path();
        fs::write(p.join(".gitignore"), "*.log\n").unwrap();
        fs::write(p.join("debug.log"), "x").unwrap();

        let repo = Repo::open(p).unwrap();
        let files = repo.status().unwrap();
        assert!(files.iter().all(|f| f.path != "debug.log"));
        assert_eq!(find(&files, ".gitignore").state, FileState::Untracked);
    }

    #[test]
    fn paths_are_relative_to_repo_root_from_subdirectory() {
        let dir = init_repo();
        let sub = dir.path().join("src");
        fs::create_dir(&sub).unwrap();
        fs::write(sub.join("main.rs"), "fn main() {}").unwrap();

        // Open from the subdirectory: paths must still be root-relative.
        let repo = Repo::open(&sub).unwrap();
        let files = repo.status().unwrap();
        assert!(files.iter().any(|f| f.path == "src/main.rs"));
    }
}
