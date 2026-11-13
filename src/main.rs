mod git;

fn main() {
    print!("{}", String::from_utf8_lossy(&git::diff().unwrap().stdout));
}
