import curses
import abc
from typing import List

from settings import HELLO_HEADER

KEY_ESC = 27

NEED_EXIT = 1
NEED_KEY = 2


class AbstractItemType(metaclass=abc.ABCMeta):
    def press(self):
        pass


class Item:
    def __init__(self,
                 name: str,
                 comment: str
                 ):
        self.name = name
        self.comment = comment


class Menu:
    def __init__(self, stdscr):
        self._init_curses(stdscr)

        self._items = []  # type: List[Item]
        self._active_item = 0

    def _init_curses(self, stdscr):
        self.stdscr = stdscr
        curses.start_color()
        curses.use_default_colors()

        self._init_colors()

        self.stdscr.clear()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def _init_colors(self):
        curses.init_pair(1, -1, 0)  # White on Black
        self.TEXT = curses.color_pair(1)

        curses.init_pair(2, 0, 7)  # Black on White
        self.ACTIVE_TEXT = curses.color_pair(2)

        curses.init_pair(3, 8, 0)  # Gray on Black
        self.COMMENT = curses.color_pair(3)

    @property
    def width(self):
        return self.stdscr.getmaxyx()[1]

    @property
    def height(self):
        return self.stdscr.getmaxyx()[0]

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        self._items = items
        self.active_item = 0

    @property
    def active_item(self):
        return self._active_item

    @active_item.setter
    def active_item(self, value: int):
        length = len(self.items)
        if 0 != length:
            self._active_item = value % length

    def render(self):
        self.stdscr.addstr(0, 0, "> Матан > Дифференциальные уровнения")
        self.stdscr.addstr(1, 0, "=" * self.width)
        self.stdscr.addstr(0, self.width - len(HELLO_HEADER) - 1, HELLO_HEADER)

        for i, item in enumerate(self.items):
            color = self.ACTIVE_TEXT if i == self.active_item else self.TEXT
            y = (i + 1) * 3
            self.stdscr.addstr(y, 0, item.name, color)
            self.stdscr.addstr(y + 1, 2, item.comment[:30], self.COMMENT)

    def key_handle(self, key):
        if curses.KEY_DOWN == key:
            self.active_item += 1
        elif curses.KEY_UP == key:
            self.active_item -= 1
        elif KEY_ESC == key or ord('q') == key:
            return NEED_EXIT

        return NEED_KEY

    def redraw(self):
        self.stdscr.refresh()

    def __del__(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()

        curses.endwin()
