#!/usr/bin/env python3

from curses import wrapper

from menu import Item, Menu, NEED_KEY


def main(stdscr):
    item1 = Item("Это первый тестовый вариант", "Comment1")
    item2 = Item("Это второй", "Comment1")
    item3 = Item("Ну а это третий", "Comment1")

    menu = Menu(stdscr)
    menu.items = [item1, item2, item3]

    status = NEED_KEY
    while NEED_KEY == status:
        menu.render()
        key = stdscr.getch()
        status = menu.key_handle(key)
        menu.redraw()

wrapper(main)
