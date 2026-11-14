use std::process::Command;

pub(crate) fn diff() -> std::result::Result<String, std::io::Error> {
    let output = Command::new("git").arg("diff").output()?;
    Ok(String::from_utf8_lossy(&output.stdout).into_owned())
}

pub(crate) fn diff_file(file_path: &str) -> Result<String, std::io::Error> {
    let output = Command::new("git").args(["diff", file_path]).output()?;
    Ok(String::from_utf8_lossy(&output.stdout).into_owned())
}
