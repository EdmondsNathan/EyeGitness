use crate::app::git::{ConflictKind, FileState, FileStatus, GitError, GitFile};

pub(super) fn status(output: &str) -> Result<Vec<GitFile>, GitError> {
    let mut files: Vec<GitFile> = Vec::new();

    for line in output.split('\0') {
        if line.is_empty() {
            continue;
        }

        let mut chars = line.chars();

        let (Some(x), Some(y)) = (chars.next(), chars.next()) else {
            return Err(GitError::Parse("Malformed status line".to_owned()));
        };
    }

    todo!()
}

fn parse_xy(x: char, y: char) -> Result<FileState, GitError> {
    use ConflictKind::*;

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
