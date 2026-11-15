mod git;

fn main() {
    println!("\n\n");

    // print!("{}", git::diff().unwrap());

    // print!("{}", git::diff_file("src/git/mod.rs").unwrap());

    // for file_name in git::files::untracked_files().unwrap() {
    //     println!("{}", file_name);
    // }

    // for file_name in git::files::modified_files().unwrap() {
    //     println!("{}", file_name);
    // }

    // for file_name in git::files::modified_files().unwrap() {
    //     println!("MODIFED FILE: {}", file_name);
    //
    //     print!("{}\n\n", git::diff_file(&file_name).unwrap());
    // }

    // for file_name in git::files::untracked_files().unwrap() {
    //     println!("UNTRACKED FILE: {}", file_name);
    //
    //     println!("{}", std::fs::read_to_string(file_name).unwrap());
    // }
}
