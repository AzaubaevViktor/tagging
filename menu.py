import curses
import abc
from typing import List


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
        self.stdscr.clear()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        # init colors
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

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
        for i, item in enumerate(self.items):
            color = curses.A_REVERSE if i == self.active_item else curses.COLOR_WHITE
            self.stdscr.addstr(i * 3, 0, item.name, color)

    def key_handle(self, key):
        if curses.KEY_DOWN == key:
            self.active_item += 1
        elif curses.KEY_UP == key:
            self.active_item -= 1
        elif KEY_ESC == key:
            return NEED_EXIT

        return NEED_KEY

    def redraw(self):
        self.stdscr.refresh()

    def __del__(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()

        curses.endwin()
