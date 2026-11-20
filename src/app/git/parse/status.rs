use std::str::Split;

use crate::app::git::{ConflictKind, FileState, FileStatus, GitError, GitFile};

pub(crate) const STATUS_ARGS: &[&str] = &["status", "--porcelain", "-z", "--untracked-files=all"];

pub(crate) fn status(output: &str) -> Result<Vec<GitFile>, GitError> {
    let mut files: Vec<GitFile> = Vec::new();
    let mut fields = output.split('\0');

    while let Some(record) = fields.next() {
        if record.is_empty() {
            continue;
        }

        files.push(parse_file(record, &mut fields)?);
    }

    Ok(files)
}

fn parse_file(record: &str, fields: &mut Split<'_, char>) -> Result<GitFile, GitError> {
    let mut chars = record.chars();

    let (Some(x), Some(y)) = (chars.next(), chars.next()) else {
        return Err(GitError::Parse(format!("Malformed record {record}")));
    };

    let path = record
        .get(3..)
        .ok_or_else(|| GitError::Parse(format!("Malformed record {record}")))?
        .to_owned();

    let state = parse_xy(x, y)?;

    let orig_path = if has_orig_path(&state) {
        match fields.next() {
            Some(path) => Some(path.to_owned()),
            None => {
                return Err(GitError::Parse(format!("Malformed record {record}")));
            }
        }
    } else {
        None
    };

    Ok(GitFile {
        path,
        orig_path,
        state,
    })
}

fn has_orig_path(state: &FileState) -> bool {
    match state {
        FileState::Normal {
            index,
            working_tree,
        } => {
            matches!(index, Some(FileStatus::Renamed | FileStatus::Copied))
                || matches!(working_tree, Some(FileStatus::Renamed | FileStatus::Copied))
        }
        _ => false,
    }
}

fn parse_xy(x: char, y: char) -> Result<FileState, GitError> {
    use ConflictKind::{
        AddedByThem, AddedByUs, BothAdded, BothDeleted, BothModified, DeletedByThem, DeletedByUs,
    };

    Ok(match (x, y) {
        ('?', '?') => FileState::Untracked,
        ('D', 'D') => FileState::Conflicted(BothDeleted),
        ('A', 'U') => FileState::Conflicted(AddedByUs),
        ('U', 'D') => FileState::Conflicted(DeletedByThem),
        ('U', 'A') => FileState::Conflicted(AddedByThem),
        ('D', 'U') => FileState::Conflicted(DeletedByUs),
        ('A', 'A') => FileState::Conflicted(BothAdded),
        ('U', 'U') => FileState::Conflicted(BothModified),
        _ => FileState::Normal {
            index: status_from_char(x)?,
            working_tree: status_from_char(y)?,
        },
    })
}

fn status_from_char(c: char) -> Result<Option<FileStatus>, GitError> {
    Ok(match c {
        ' ' => None,
        'M' => Some(FileStatus::Modified),
        'T' => Some(FileStatus::TypeChanged),
        'A' => Some(FileStatus::Added),
        'D' => Some(FileStatus::Deleted),
        'R' => Some(FileStatus::Renamed),
        'C' => Some(FileStatus::Copied),
        other => return Err(GitError::Parse(format!("Malformed status char {other}"))),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn file(path: &str, orig_path: Option<&str>, state: FileState) -> GitFile {
        GitFile {
            path: path.to_owned(),
            orig_path: orig_path.map(str::to_owned),
            state,
        }
    }

    fn normal(index: Option<FileStatus>, working_tree: Option<FileStatus>) -> FileState {
        FileState::Normal {
            index,
            working_tree,
        }
    }

    // ---- status(): whole-output behavior ----

    #[test]
    fn empty_output() {
        assert!(status("").unwrap().is_empty());
    }

    #[test]
    fn modified_unstaged() {
        let files = status(" M src/main.rs\0").unwrap();
        assert_eq!(
            files,
            vec![file(
                "src/main.rs",
                None,
                normal(None, Some(FileStatus::Modified))
            )]
        );
    }

    #[test]
    fn staged_only() {
        let files = status("M  src/lib.rs\0").unwrap();
        assert_eq!(
            files,
            vec![file(
                "src/lib.rs",
                None,
                normal(Some(FileStatus::Modified), None)
            )]
        );
    }

    #[test]
    fn staged_and_modified() {
        let files = status("MM both.rs\0").unwrap();
        assert_eq!(
            files,
            vec![file(
                "both.rs",
                None,
                normal(Some(FileStatus::Modified), Some(FileStatus::Modified))
            )]
        );
    }

    #[test]
    fn added_then_modified() {
        let files = status("AM new.rs\0").unwrap();
        assert_eq!(
            files[0].state,
            normal(Some(FileStatus::Added), Some(FileStatus::Modified))
        );
    }

    #[test]
    fn deleted_unstaged_and_staged() {
        let files = status(" D gone.rs\0D  removed.rs\0").unwrap();
        assert_eq!(files[0].state, normal(None, Some(FileStatus::Deleted)));
        assert_eq!(files[1].state, normal(Some(FileStatus::Deleted), None));
    }

    #[test]
    fn type_changed() {
        let files = status(" T link\0").unwrap();
        assert_eq!(files[0].state, normal(None, Some(FileStatus::TypeChanged)));
    }

    #[test]
    fn untracked_with_spaces_in_name() {
        let files = status("?? new file.txt\0").unwrap();
        assert_eq!(
            files,
            vec![file("new file.txt", None, FileState::Untracked)]
        );
    }

    #[test]
    fn non_ascii_path() {
        let files = status(" M café/日本語.rs\0").unwrap();
        assert_eq!(files[0].path, "café/日本語.rs");
    }

    #[test]
    fn multiple_records_keep_order() {
        let files = status(" M a.rs\0M  b.rs\0?? c.rs\0").unwrap();
        let paths: Vec<&str> = files.iter().map(|f| f.path.as_str()).collect();
        assert_eq!(paths, vec!["a.rs", "b.rs", "c.rs"]);
    }

    // ---- renames and copies ----

    #[test]
    fn rename_consumes_orig_path() {
        let files = status("R  new.rs\0old.rs\0").unwrap();
        assert_eq!(
            files,
            vec![file(
                "new.rs",
                Some("old.rs"),
                normal(Some(FileStatus::Renamed), None)
            )]
        );
    }

    #[test]
    fn record_after_rename_still_parses() {
        // Proves the extra field is consumed and not treated as a record.
        let files = status("R  new.rs\0old.rs\0 M other.rs\0").unwrap();
        assert_eq!(files.len(), 2);
        assert_eq!(files[1].path, "other.rs");
        assert_eq!(files[1].orig_path, None);
    }

    #[test]
    fn copy_consumes_orig_path() {
        let files = status("C  copy.rs\0src.rs\0").unwrap();
        assert_eq!(files[0].orig_path.as_deref(), Some("src.rs"));
        assert_eq!(files[0].state, normal(Some(FileStatus::Copied), None));
    }

    #[test]
    fn rename_with_worktree_edit() {
        let files = status("RM new.rs\0old.rs\0").unwrap();
        assert_eq!(
            files[0].state,
            normal(Some(FileStatus::Renamed), Some(FileStatus::Modified))
        );
        assert_eq!(files[0].orig_path.as_deref(), Some("old.rs"));
    }

    #[test]
    fn rename_missing_orig_path_is_error() {
        // No field follows the rename record at all.
        assert!(matches!(status("R  new.rs"), Err(GitError::Parse(_))));
    }

    // ---- conflicts ----

    #[test]
    fn all_seven_conflict_codes() {
        let cases = [
            ("UU", ConflictKind::BothModified),
            ("AA", ConflictKind::BothAdded),
            ("DD", ConflictKind::BothDeleted),
            ("AU", ConflictKind::AddedByUs),
            ("UA", ConflictKind::AddedByThem),
            ("DU", ConflictKind::DeletedByUs),
            ("UD", ConflictKind::DeletedByThem),
        ];
        for (code, kind) in cases {
            let output = format!("{code} c.rs\0");
            let files = status(&output).unwrap();
            assert_eq!(files[0].state, FileState::Conflicted(kind), "code {code}");
            assert_eq!(files[0].orig_path, None);
        }
    }

    // ---- malformed input ----

    #[test]
    fn short_record_is_error() {
        assert!(matches!(status("x\0"), Err(GitError::Parse(_))));
        assert!(matches!(status("M\0"), Err(GitError::Parse(_))));
    }

    #[test]
    fn unknown_status_char_is_error() {
        assert!(matches!(status("Z  file.rs\0"), Err(GitError::Parse(_))));
    }

    #[test]
    fn partial_conflict_code_is_error() {
        // 'U' paired with a non-conflict partner isn't one of the seven codes.
        assert!(matches!(status("UM file.rs\0"), Err(GitError::Parse(_))));
    }

    #[test]
    fn ignored_is_error_since_not_requested() {
        assert!(matches!(status("!! target/\0"), Err(GitError::Parse(_))));
    }

    // ---- parse_xy ----

    #[test]
    fn xy_untracked() {
        assert_eq!(parse_xy('?', '?').unwrap(), FileState::Untracked);
    }

    #[test]
    fn xy_blank_blank_is_normal_with_no_changes() {
        assert_eq!(parse_xy(' ', ' ').unwrap(), normal(None, None));
    }

    #[test]
    fn xy_half_untracked_is_error() {
        assert!(parse_xy('?', 'M').is_err());
    }

    // ---- status_from_char ----

    #[test]
    fn char_mapping() {
        assert_eq!(status_from_char(' ').unwrap(), None);
        assert_eq!(status_from_char('M').unwrap(), Some(FileStatus::Modified));
        assert_eq!(
            status_from_char('T').unwrap(),
            Some(FileStatus::TypeChanged)
        );
        assert_eq!(status_from_char('A').unwrap(), Some(FileStatus::Added));
        assert_eq!(status_from_char('D').unwrap(), Some(FileStatus::Deleted));
        assert_eq!(status_from_char('R').unwrap(), Some(FileStatus::Renamed));
        assert_eq!(status_from_char('C').unwrap(), Some(FileStatus::Copied));
    }

    #[test]
    fn char_unknown_is_error() {
        assert!(status_from_char('Z').is_err());
        assert!(status_from_char('U').is_err()); // only valid inside conflict pairs
        assert!(status_from_char('?').is_err());
    }

    // ---- has_orig_path ----

    #[test]
    fn has_orig_path_only_for_rename_or_copy() {
        assert!(has_orig_path(&normal(Some(FileStatus::Renamed), None)));
        assert!(has_orig_path(&normal(None, Some(FileStatus::Copied))));
        assert!(!has_orig_path(&normal(Some(FileStatus::Modified), None)));
        assert!(!has_orig_path(&FileState::Untracked));
        assert!(!has_orig_path(&FileState::Conflicted(
            ConflictKind::BothModified
        )));
    }
}
