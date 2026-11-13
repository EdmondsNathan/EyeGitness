use std::process::Command;

pub(crate) fn diff() -> std::result::Result<std::process::Output, std::io::Error> {
    Command::new("git").arg("diff").output()
}
