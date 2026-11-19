# EyeGitness
A keyboard-driven TUI for managing your Git repos
## Status
EyeGitness is currently being rewritten from scratch in Rust. The Rust version is in **early pre-alpha** and is NOT yet ready for general use.
The original Python release is available [here](https://github.com/EdmondsNathan/EyeGitness/releases/tag/v1.0.0).
## Why Rewrite?
The original Python version was running into performance issues on larger files and repos. The architecture also made extending functionality difficult.
The Rust rewrite aims to fix both of these issues with better performance and a better foundation for future extension.
## Roadmap
### v2.0.0: Feature Parity
Match the functionality of the original Python release
- [ ] Add, stage, and reset files
- [ ] Commit changes
- [ ] View diffs
### Future Versions
Expand EyeGitness with more functionality
#### Customization
- [ ] Remappable keys
- [ ] Custom commands with configurable keys
#### Expanded Git Support
- [ ] Inspect logs
- [ ] Pushing to remote
- [ ] Restore files
- [ ] Checkout
- [ ] Branch management(switch, merge, resolve conflicts)
- [ ] Hunk as well as per-line staging
- [ ] Undo support
