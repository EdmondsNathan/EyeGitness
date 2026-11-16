pub(crate) enum GitError {
    Io(std::io::Error),
    Git(String),
    Parse(String),
}

impl std::fmt::Display for GitError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            GitError::Io(error) => write!(f, "{}", error),
            GitError::Git(error) => write!(f, "{}", error),
            GitError::Parse(error) => write!(f, "{}", error),
        }
    }
}
