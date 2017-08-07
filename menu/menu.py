import curses
from typing import List

from settings import HELLO_HEADER
from curses_wrapper import colors
from .statuses import NEED_KEY, NEED_EXIT

KEY_ESC = 27


class Menu:
    def __init__(self, stdscr):
        self.stdscr = stdscr

        self._items = []  # type: List[SimpleItem]
        self._active_item = 0

    @property
    def width(self):
        return self.stdscr.getmaxyx()[1]

    @property
    def height(self):
        return self.stdscr.getmaxyx()[0]

    @property
    def items(self):
        return self._items

    def add_item(self, item: "SimpleItem"):
        self._items.append(item)

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
            color = colors.ACTIVE_TEXT if i == self.active_item else colors.TEXT
            y = (i + 1) * 2
            self.stdscr.addstr(y, 0, "{:}: {}".format(i, item.name), color)
            self.stdscr.addstr(y + 1, 2, item.comment[:30], colors.COMMENT)

    def key_handle(self, key):
        key = ord(key) if isinstance(key, str) else key

        if curses.KEY_DOWN == key:
            self.active_item += 1
        elif curses.KEY_UP == key:
            self.active_item -= 1
        elif KEY_ESC == key:
            return NEED_EXIT

        return NEED_KEY

    def refresh(self):
        self.stdscr.refresh()

    def __del__(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()

        curses.endwin()
