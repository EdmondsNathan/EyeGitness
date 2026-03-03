#!/usr/bin/env python3
import curses
import subprocess

# TAG_TODO add -h or --help screen that's also accessible with ? in the program
def main(stdscr: curses.window):
    curses.use_default_colors()
    curses.curs_set(False)
    stdscr.nodelay(True)
    stdscr.clear()

    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(0)

    scroll_offset = 0
    lines = 0

    curses.init_pair(0, -1, -1)
    # curses.init_pair(1, -1, curses.COLOR_GREEN)
    # curses.init_pair(2, -1, curses.COLOR_RED)
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)

    while True:
        # First command: git diff
        diff = subprocess.Popen(
            ["git", "diff"],
            stdout=subprocess.PIPE
        )

        # Second command: grep
        grep = subprocess.run(
            ["grep", "-e", r"^-\+", "-e", r"^\+\+",],# "--color=always"],
            # ["grep", ""],
            stdin=diff.stdout,
            capture_output=True,
            text=True
        ).stdout

        if(len(grep.splitlines()) != lines):
            lines = len(grep.splitlines())
            scroll_offset = 0

        try:
            key = stdscr.getch()
        except:
            key = None

        scroll_up = False
        scroll_down = False
        try:
            mouse = _, _, _, _, button_state = curses.getmouse()

            if button_state & curses.BUTTON4_PRESSED:
                scroll_up = True
            elif button_state & curses.BUTTON5_PRESSED:
                scroll_down = True
        except:
            pass

        if key == ord("q"):
            quit()
        elif key == ord("j") or scroll_down:
            scroll_offset = min(scroll_offset + 1, lines - curses.LINES - 1)
        elif key == ord("k") or scroll_up:
            scroll_offset = max(scroll_offset - 1, 0)
        elif key == ord("g"):
            scroll_offset = 0
        elif key == ord("G"):
            scroll_offset = lines - curses.LINES - 1
        elif key == ord("d"):
            scroll_offset = min(scroll_offset + int(curses.LINES / 2), lines - curses.LINES - 1)
        elif key == ord("u"):
            scroll_offset = max(scroll_offset - int(curses.LINES / 2), 0)
        elif key == ord("n"):
            # TAG_TODO Jump between files, count the lines that contain --- or +++(skipping sequential ones)
            # Count back through the list and store if the line count is greater than scroll_offset
            # Default to 0 in case all are above cursor
            pass
        elif key == ord("N"):
            pass
        elif key == ord("?"):
            # TAG_TODO help screen with shortcuts
            pass

        pad = curses.newpad(lines + 1, 200)

        output = grep.splitlines()
        if lines > 0:
            for n in range(lines):
                attribute = 0
                colors = 0
                if output[n].startswith("+++") or output[n].startswith("---"):
                    attribute = curses.A_REVERSE
                elif output[n].startswith("+"):
                    colors = 1
                elif output[n].startswith("-"):
                    colors = 2
                else:
                    curses.init_pair(1, -1, -1)
                pad.addstr(n, 0, output[n], curses.color_pair(colors) | attribute)
        else:
            stdscr.erase()
        # pad.addstr(grep)

        # pad.refresh(scroll_offset, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)
        try:
            pad.refresh(scroll_offset, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)
        except curses.error:
            stdscr.refresh()

curses.wrapper(main)
