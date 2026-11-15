pub(crate) enum GitError {
    Io(std::io::Error),
    Git(String),
}
