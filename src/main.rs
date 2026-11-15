mod git;

fn main() {
    let output = match git::modified_files() {
        Ok(result) => result.join("\n"),
        Err(error) => error.to_string(),
    };

    print!("{}", output);
}
