"""ANSI escape code constants for terminal styling."""

_ESC = "\033["

RESET = f"{_ESC}0m"
BOLD = f"{_ESC}1m"
DIM = f"{_ESC}2m"
INVERT = f"{_ESC}7m"

RED = f"{_ESC}31m"
GREEN = f"{_ESC}32m"
YELLOW = f"{_ESC}33m"
CYAN = f"{_ESC}36m"
