import curses
from typing import List

from settings import HELLO_HEADER
from curses_wrapper import colors, print_effect
from natsort import natsorted, ns

from .items import TagItem, AbstractItemType
from .statuses import NEED_KEY, NEED_EXIT

KEY_ESC = 27
KEY_ENTER = 10


class Menu:
    def __init__(self, stdscr, tag_manager: "TagManager"):
        self.stdscr = stdscr
        self.manager = tag_manager

        self._items = []  # type: List[AbstractItemType]

        self.update_items(reset_position=True)

        self._pos = 0

    @property
    def width(self) -> int:
        return self.stdscr.getmaxyx()[1]

    @property
    def height(self) -> int:
        return self.stdscr.getmaxyx()[0]

    def update_items(self, reset_position=False):
        self.items = self.manager.items
        self.manager.save()
        if reset_position:
            self.pos = 0
        else:
            # Сделано для корректного обновления позиции в случае изменения
            # количества элементов
            self.pos = self.pos

    @property
    def items(self) -> List[AbstractItemType]:
        return self._items

    def add_item(self, item):
        self.manager.add_item_to_cur_tag(item)
        self.update_items()

    @items.setter
    def items(self, items):
        self._items = items
        self._items = natsorted(self._items, alg=ns.IGNORECASE, key=lambda x: x.name)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value: int):
        length = len(self.items)
        if 0 != length:
            self._pos = value % length

    @property
    def active_item(self) -> AbstractItemType or None:
        if not self.items:
            return None
        return self.items[self.pos]

    def delete_item(self):
        self.manager.delete_item(self.active_item.source)
        self.update_items()

    def _get_start_item(self):
        """ Для красивой прокрутки """
        size = (self.height - 5) // 2
        start_item = 0
        if self.pos < size // 2:
            pass
        elif self.pos > len(self.items) - size + size // 2:
            start_item = max(len(self.items) - size, 0)
        else:
            start_item = self.pos - size // 2

        return start_item, start_item + size

    def render(self):
        self.stdscr.addstr(0, 0, self.manager.path)
        self.stdscr.addstr(1, 0, "=" * self.width)
        self.stdscr.addstr(0, self.width - len(HELLO_HEADER) - 1, HELLO_HEADER)

        start_item, end_item = self._get_start_item()

        for i, item in zip(
                range(start_item, end_item),
                self.items[start_item:end_item]):
            color = colors.ACTIVE_TEXT if i == self.pos else colors.TEXT

            if isinstance(self.items[i], TagItem):
                color |= curses.A_BOLD

            y = ((i - start_item) + 1) * 2

            header = item.header
            header_low = item.header_low
            about = item.about

            self.stdscr.addstr(y, 0, "{:}: {}".format(i, header[:self.width - 4]), color)
            if len(header) < self.width - 4:
                self.stdscr.addstr(y, len(header) + 1 + len(str(i)) + 2,
                                   header_low[:self.width - len(header) - len(str(i)) - 3],
                                   colors.COMMENT
                                   )
            self.stdscr.move(y+1, 2)
            if not isinstance(item, TagItem):
                s = "&3" + " ".join(["_{}_".format(tag_name) for tag_name in item.tags]) + " "
                print_effect(self.stdscr, y+1, 2, s)

            self.stdscr.addstr(item.about, colors.COMMENT)

    def key_handle(self, key):
        key = ord(key) if isinstance(key, str) else key

        if curses.KEY_DOWN == key:
            self.pos += 1
        elif curses.KEY_UP == key:
            self.pos -= 1
        elif KEY_ESC == key:
            return NEED_EXIT
        elif ord('\n') == key or curses.KEY_RIGHT == key:
            reset_position = False
            if self.items:
                reset_position = self.items[self.pos].press()
            self.update_items(reset_position=reset_position)
        elif curses.KEY_LEFT == key:
            self.manager.up()
            self.update_items(reset_position=True)

        return NEED_KEY

    def refresh(self):
        self.stdscr.refresh()

    def __del__(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()

        curses.endwin()
