use std::str::Split;

use crate::app::git::{ConflictKind, FileState, FileStatus, GitError, GitFile};

pub(super) fn status(output: &str) -> Result<Vec<GitFile>, GitError> {
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

// TODO tests
