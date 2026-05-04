"""ANSI escape code constants for terminal styling.

These are raw SGR (Select Graphic Rendition) sequences used throughout the app
to colorize diff output, highlight selections, and style the status bar.
"""

_ESC = "\033["  # CSI (Control Sequence Introducer) prefix

# Text attributes
RESET = f"{_ESC}0m"   # Clear all styling
BOLD = f"{_ESC}1m"    # Bold / increased intensity
DIM = f"{_ESC}2m"     # Faint / decreased intensity
INVERT = f"{_ESC}7m"  # Swap foreground and background colors

# Foreground colors
RED = f"{_ESC}31m"     # Diff deletions
GREEN = f"{_ESC}32m"   # Diff additions, section titles
YELLOW = f"{_ESC}33m"  # Commit hashes, selection counts
CYAN = f"{_ESC}36m"    # Hunk headers (@@), HEAD decoration
