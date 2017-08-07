#!/usr/bin/env python3

import locale

from tag import TagManager

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

from curses import wrapper
import curses_wrapper as cw

from console import Console
from menu import SimpleItem, Menu, NEED_KEY, LinkItem, FileItem


def main(stdscr):
    item1 = SimpleItem("Это первый тестовый вариант", "Comment1")
    item2 = SimpleItem("Это второй", "Comment1")
    item3 = SimpleItem("Ну а это третий", "Comment1")
    link = LinkItem("Ссылка", "Описание страницы", "http://google.ru")
    file = FileItem("Файл", "Описание файла", "~")

    cw.init(stdscr)

    tag_manager = TagManager()

    menu = Menu(stdscr, tag_manager)
    # menu.items = [item1, item2, item3, link, file]

    console = Console(stdscr)
    console.menu = menu

    status = NEED_KEY
    while NEED_KEY == status:

        stdscr.clear()

        menu.render()
        console.render()

        menu.refresh()
        console.refresh()

        key = stdscr.get_wch()

        status = menu.key_handle(key)
        console.key_handle(key)



wrapper(main)
