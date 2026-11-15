use std::process::Command;

pub enum GitError {
    Io(std::io::Error),
    Git { stderr: String },
}

impl From<std::io::Error> for GitError {
    fn from(error: std::io::Error) -> Self {
        GitError::Io(error)
    }
}

fn run_git(args: &[&str]) -> Result<Vec<u8>, GitError> {
    let output = Command::new("git").args(args).output()?;

    if !output.status.success() {
        return Err(GitError::Git {
            stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
        });
    }

    Ok(output.stdout)
}
