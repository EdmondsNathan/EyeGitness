pub(crate) struct GitFile {
    pub(crate) path: String,
    pub(crate) orig_path: Option<String>,
    pub(crate) state: FileState,
}

pub(crate) enum FileState {
    Normal {
        index: Option<FileStatus>,
        working_tree: Option<FileStatus>,
    },
    Untracked,
    Conflicted(ConflictKind),
}

pub(crate) enum FileStatus {
    Modified,    // M
    TypeChanged, // T
    Added,       // A
    Deleted,     // D
    Renamed,     // R
    Copied,      // C
}

pub(crate) enum ConflictKind {
    BothDeleted,   // DD
    AddedByUs,     // AU
    DeletedByThem, // UD
    AddedByThem,   // UA
    DeletedByUs,   // DU
    BothAdded,     // AA
    BothModified,  // UU
}
