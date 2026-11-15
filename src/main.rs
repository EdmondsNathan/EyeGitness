mod git;

fn main() {
    let output = match git::diff_file("src/main.rs") {
        Ok(result) => result,
        Err(error) => error.to_string(),
    };

    print!("{}", output);
}
