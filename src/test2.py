from ansi.codes import RESET, RED, GREEN, INVERT
from ansi.colorizer import diff_colorize
from git.diff import diff_unstaged


print(diff_colorize(diff_unstaged()))
