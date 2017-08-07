import curses
from typing import List

from settings import HELLO_HEADER
from curses_wrapper import colors
from .items import TagItem
from .statuses import NEED_KEY, NEED_EXIT

KEY_ESC = 27
KEY_ENTER = 10


class Menu:
    def __init__(self, stdscr, tag_manager: "TagManager"):
        self.stdscr = stdscr
        self.manager = tag_manager

        self._items = []  # type: List["AbstractItem"]

        self.update_items()

        self._pos = 0

    @property
    def width(self):
        return self.stdscr.getmaxyx()[1]

    @property
    def height(self):
        return self.stdscr.getmaxyx()[0]

    def update_items(self):
        self.items = self.manager.items

    @property
    def items(self):
        return self._items

    def add_item(self, item: "SimpleItem"):
        self._items.append(item)

    @items.setter
    def items(self, items):
        self._items = items
        self.pos = 0

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value: int):
        length = len(self.items)
        if 0 != length:
            self._pos = value % length

    def render(self):
        self.stdscr.addstr(0, 0, self.manager.path)
        self.stdscr.addstr(1, 0, "=" * self.width)
        self.stdscr.addstr(0, self.width - len(HELLO_HEADER) - 1, HELLO_HEADER)

        for i, item in enumerate(self.items):
            color = colors.ACTIVE_TEXT if i == self.pos else colors.TEXT

            if isinstance(self.items[i], TagItem):
                color |= curses.A_BOLD

            y = (i + 1) * 2
            self.stdscr.addstr(y, 0, "{:}: {}".format(i, item.name), color)
            self.stdscr.addstr(y + 1, 2, item.comment[:30], colors.COMMENT)

    def key_handle(self, key):
        key = ord(key) if isinstance(key, str) else key

        if curses.KEY_DOWN == key:
            self.pos += 1
        elif curses.KEY_UP == key:
            self.pos -= 1
        elif KEY_ESC == key:
            return NEED_EXIT
        elif curses.KEY_RIGHT == key:
            self.items[self.pos].press()
            self.update_items()
        elif curses.KEY_LEFT == key:
            self.manager.up()
            self.update_items()

        return NEED_KEY

    def refresh(self):
        self.stdscr.refresh()

    def __del__(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()

        curses.endwin()
