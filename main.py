#!/usr/bin/env python3

import locale

import os

from tag import TagManager

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

from curses import wrapper
import curses_wrapper as cw

from console import Console
from menu import SimpleItem, Menu, NEED_KEY, LinkItem, FileItem


os.environ.setdefault('ESCDELAY', '25')

def main(stdscr):
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

        console.key_handle(key)
        if not console.is_handle_key:
            status = menu.key_handle(key)



wrapper(main)
