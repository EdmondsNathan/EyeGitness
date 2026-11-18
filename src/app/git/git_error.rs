#[derive(Debug, thiserror::Error)]
pub(crate) enum GitError {
    #[error("failed to run git: {0}")]
    Io(#[from] std::io::Error),
    #[error("Git failed: {0}")]
    Git(String),
    #[error("Parser failed: {0}")]
    Parse(String),
}
