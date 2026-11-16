pub(crate) struct GitFile {
    pub path: String,
    pub staged_status: Option<FileStatus>,
    pub unstaged_status: Option<FileStatus>,
}

pub(crate) enum FileStatus {
    Added,
    Modified,
    Untracked,
    Deleted,
    Renamed,
    Conflict,
}
