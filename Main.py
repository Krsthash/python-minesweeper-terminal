#!/usr/bin/env python
"""
Minesweeper written in Python to be played in a terminal.
"""

import time
import threading
import curses
from curses import textpad
from GameMap import GameMap as Gm


def draw_footer(stdscr, message):
    y, x = stdscr.getmaxyx()
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)
    stdscr.attron(curses.color_pair(3))
    footer_text = f"{message} | n - New game    o - Options    q - Quit"
    stdscr.addstr(y - 2, 0, footer_text + " " * (x - len(footer_text)))
    stdscr.attroff(curses.color_pair(3))
    stdscr.refresh()


def draw_options(stdscr, selected):
    maxy, maxx = stdscr.getmaxyx()
    opts = ["-Easy(9x9)", "-Intermediate(16x16)", "-Expert(30x16)", "-Custom"]
    win3 = curses.newwin(10, 30, (maxy//2)-5, (maxx//2)-15)
    textpad.rectangle(win3, 0, 0, 8, 29)
    win3.addstr(0, 2, "Options")
    win3.addstr(1, 1, "Size:")
    for idx, opt in enumerate(opts):
        if idx == selected:
            curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
            win3.attron(curses.color_pair(4))
            win3.addstr(idx + 2, 1, str(opt))
            win3.attroff(curses.color_pair(4))
        else:
            win3.addstr(idx + 2, 1, str(opt))
    win3.refresh()


def draw_custom(stdscr, selected, enter, custom_opts):
    maxy, maxx = stdscr.getmaxyx()
    opts = ["-Width:", "-Height:", "-Mines:", "Save"]
    win4 = curses.newwin(10, 30, (maxy // 2) - 5, (maxx // 2) - 15)
    textpad.rectangle(win4, 0, 0, 8, 29)
    win4.addstr(0, 2, "Options")
    win4.addstr(1, 1, "Custom size:")
    for idx, opt in enumerate(opts):
        if idx == selected:
            curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
            win4.attron(curses.color_pair(4))
            if idx != 3:
                win4.addstr(idx + 2, 1, str(opt) + f" {custom_opts[idx]}")
            else:
                win4.addstr(idx + 2, 1, str(opt))
            win4.attroff(curses.color_pair(4))
        else:
            if idx != 3:
                win4.addstr(idx + 2, 1, str(opt) + f" {custom_opts[idx]}")
            else:
                win4.addstr(idx + 2, 1, str(opt))
    if enter:
        curses.echo()
        s = ""
        while not s.isnumeric():
            win4.addstr(selected + 2, len(opts[selected]) + 2, "   ")
            s = str(win4.getstr(selected + 2, len(opts[selected]) + 2, 3).decode("utf-8"))
            stdscr.refresh()
        curses.noecho()
        return s
    win4.refresh()


def custom(stdscr):
    global height
    global width
    global mines
    selected = 0
    custom_opts = [0, 0, 0]
    while True:
        draw_custom(stdscr, selected, False, custom_opts)
        key = stdscr.getch()
        if key == curses.KEY_DOWN and selected < 3:
            selected += 1
            draw_custom(stdscr, selected, False, custom_opts)
        elif key == curses.KEY_UP and selected > 0:
            selected -= 1
            draw_custom(stdscr, selected, False, custom_opts)
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            if selected == 0:
                custom_opts[selected] = int(draw_custom(stdscr, selected, True, custom_opts))
            elif selected == 1:
                custom_opts[selected] = int(draw_custom(stdscr, selected, True, custom_opts))
            elif selected == 2:
                custom_opts[selected] = int(draw_custom(stdscr, selected, True, custom_opts))
            else:
                width = custom_opts[0]
                height = custom_opts[1]
                mines = custom_opts[2]
                break


def options(stdscr, driver):
    global height
    global width
    global mines
    """
    Size:
    -Easy(9x9)
    -Intermediate(16x16)
    -Expert(30x16)
    -Custom
    """
    stdscr.clear()
    driver.draw_header(stdscr)
    draw_footer(stdscr, "Options will apply to a new game.")
    selected = 0
    draw_options(stdscr, selected)
    while True:
        key = stdscr.getch()
        if key == curses.KEY_DOWN and selected < 3:
            selected += 1
            draw_options(stdscr, selected)
        elif key == curses.KEY_UP and selected > 0:
            selected -= 1
            draw_options(stdscr, selected)
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            if selected == 0:
                height, width = 9, 9
                mines = 10
                stdscr.clear()
                break
            elif selected == 1:
                height, width = 16, 16
                mines = 40
                stdscr.clear()
                break
            elif selected == 2:
                height, width = 16, 30
                mines = 99
                stdscr.clear()
                break
            elif selected == 3:
                custom(stdscr)
                stdscr.clear()
                break


def game_over(stdscr, status):
    if status == 0:  # game over
        color = curses.COLOR_RED
        message = "You hit a mine. Game over. | Press any key to continue..."
    else:
        color = curses.COLOR_GREEN
        message = "You found all the mines. You won!"
    y, x = stdscr.getmaxyx()
    curses.init_pair(3, curses.COLOR_BLACK, color)
    stdscr.attron(curses.color_pair(3))
    footer_text = message
    stdscr.addstr(y - 4, 0, footer_text + " " * (x - len(footer_text)))
    stdscr.attroff(curses.color_pair(3))
    stdscr.refresh()


class Driver:
    def __init__(self, h, w, m):
        self.height = h
        self.width = w
        self.mines = m
        self.win = curses.newwin(h + 1, w + 1, 2, 2)
        self.win2 = curses.newwin(h + 1, w + 1, 2, 2 + w * 2)
        self.grid = Gm(w, h, m)
        self.grid.generate_mines()
        self.grid.generate_pointers()
        self.win.refresh()

    def draw_vmap(self, selectedy, selectedx):
        for y in range(self.height):
            for x in range(self.width):
                if y == selectedy and x == selectedx:
                    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                    self.win.attron(curses.color_pair(1))
                    self.win.addch(y, x, f"{self.grid.vmap[y][x]}")
                    self.win.attroff(curses.color_pair(1))
                else:
                    to_draw = self.grid.vmap[y][x]
                    if to_draw == "X":
                        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
                        self.win.attron(curses.color_pair(2))
                        self.win.addch(y, x, f"{to_draw}")
                        self.win.attroff(curses.color_pair(2))
                    else:
                        self.win.addch(y, x, f"{to_draw}")
        self.win.refresh()

    def draw_gmap(self):  # Draw the actual game map
        for y in range(self.height):
            for x in range(self.width):
                to_draw = self.grid.grid[y][x]
                if to_draw == "X":
                    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
                    self.win2.attron(curses.color_pair(2))
                    self.win2.addch(y, x, f"{to_draw}")
                    self.win2.attroff(curses.color_pair(2))
                else:
                    self.win2.addch(y, x, f"{to_draw}")
        self.win2.refresh()

    class Timer(threading.Thread):
        def __init__(self, driv, stdscr):
            super().__init__()
            self.counting = True
            self._target = self.counter
            self.daemon = True
            self.stdscr = stdscr
            self.driv = driv
            self.start()

        def stop(self):
            self.counting = False

        def counter(self):
            start_time = int(time.time())
            while self.counting:
                time_now = int(time.time())
                y, x = self.stdscr.getmaxyx()
                curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)
                self.stdscr.attron(curses.color_pair(3))
                header_text = f"Terminal Minesweeper - Size: {self.driv.height}x{self.driv.width}   " \
                              f"Mines: {self.driv.grid.mines_left}   Time: {time_now - start_time}"
                self.stdscr.addstr(0, 0, header_text + " " * (x - len(header_text)))
                self.stdscr.attroff(curses.color_pair(3))
                self.stdscr.refresh()
                time.sleep(1)

    def draw_header(self, stdscr):
        y, x = stdscr.getmaxyx()
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)
        stdscr.attron(curses.color_pair(3))
        header_text = f"Terminal Minesweeper - Size: {self.height}x{self.width}   Mines: {self.grid.mines_left}"
        stdscr.addstr(0, 0, header_text + " " * (x - len(header_text)))
        stdscr.attroff(curses.color_pair(3))
        stdscr.refresh()


def main(stdscr):
    global height
    global width
    global mines
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    driver = Driver(height, width, mines)
    footer_text = "Game driver loaded."
    stdscr.clear()
    draw_footer(stdscr, footer_text)
    stdscr.refresh()
    driver.draw_vmap(0, 0)
    footer_text = "Game map has been drawn."
    draw_footer(stdscr, footer_text)
    stdscr.refresh()

    selectedy = 0
    selectedx = 0

    timer = driver.Timer(driver, stdscr)  # Starts displaying the header timer

    try:
        while True:  # Game Mainloop
            driver.draw_vmap(selectedy, selectedx)
            key = stdscr.getch()  # Get key press

            if key == curses.KEY_DOWN and selectedy < driver.height - 1:
                selectedy += 1
                driver.draw_vmap(selectedy, selectedx)
            elif key == curses.KEY_UP and selectedy > 0:
                selectedy -= 1
                driver.draw_vmap(selectedy, selectedx)
            elif key == curses.KEY_RIGHT and selectedx < driver.width - 1:
                selectedx += 1
                driver.draw_vmap(selectedy, selectedx)
            elif key == curses.KEY_LEFT and selectedx > 0:
                selectedx -= 1
                driver.draw_vmap(selectedy, selectedx)
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                footer_text = f"Enter pressed. {selectedy} {selectedx}"
                draw_footer(stdscr, footer_text)
                if isinstance(driver.grid.vmap[selectedy][selectedx], int):  # Check if the square is a number
                    footer_text = "Opened adjacent squares."
                    draw_footer(stdscr, footer_text)
                    result = driver.grid.adjacent(selectedy, selectedx)
                    if result == 0:
                        footer_text = "You flagged an incorrect mine."
                        draw_footer(stdscr, footer_text)
                        break
                    elif result == 1:
                        footer_text = "Not enough flagged mines around the square!"
                        draw_footer(stdscr, footer_text)
                else:
                    if driver.grid.clear_tile(selectedy, selectedx) == 0:
                        footer_text = "You hit a mine."
                        draw_footer(stdscr, footer_text)
                        break
                    footer_text = "Mine cleared."
                    draw_footer(stdscr, footer_text)
            elif key == ord(" "):
                footer_text = "Space pressed."
                draw_footer(stdscr, footer_text)
                if driver.grid.vmap[selectedy][selectedx] == "X":
                    driver.grid.unmark(selectedy, selectedx)
                else:
                    if driver.grid.mark(selectedy, selectedx) == 0:
                        footer_text = "You cannot mark an opened square!"
                        draw_footer(stdscr, footer_text)
            elif key == ord("n"):
                return 0
            elif key == ord("q"):
                return 1
            elif key == ord("o"):
                options(stdscr, driver)
            driver.draw_vmap(selectedy, selectedx)
            draw_footer(stdscr, footer_text)
            driver.win.refresh()
            stdscr.refresh()
            if driver.grid.win_check() == 1:  # Game won
                game_over(stdscr, 1)
                timer.stop()
                driver.draw_gmap()
        game_over(stdscr, 0)  # Game lost
        timer.stop()
        driver.draw_gmap()
        stdscr.getch()
    finally:
        timer.stop()


if __name__ == '__main__':
    # Default values for a new game
    height = 9
    width = 9
    mines = 10
    q = 0
    while q != 1:  # If user pressed q, quit the game.
        q = curses.wrapper(main)
