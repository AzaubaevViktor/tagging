import curses


class Setter:
    def __setattr__(self, key, value):
        # super().__setattr__(key, value)
        self.__dict__[key] = value

colors = Setter()


def init(stdscr):
    curses.start_color()
    curses.use_default_colors()

    _init_colors()

    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)


def _init_colors():
    curses.init_pair(1, -1, -1)  # White on Black
    colors.TEXT = curses.color_pair(1)

    curses.init_pair(2, -1, 8)  # Black on Gray
    colors.ACTIVE_TEXT = curses.color_pair(2)

    curses.init_pair(3, 8, -1)  # Gray on Black
    colors.COMMENT = curses.color_pair(3)


def print_effect(scr, y, x, s: str, control_ch="&"):
    style = curses.A_NORMAL
    color = 0
    scr.move(y, x)

    control_mode = False

    for ch in s:
        if not control_mode:
            if "_" == ch:
                style ^= curses.A_UNDERLINE
            elif "*" == ch:
                style ^= curses.A_BOLD
            elif control_ch == ch:
                control_mode = True
            else:
                scr.addch(ch, color | style)
        else:
            if '0' <= ch <= '9':
                color = curses.color_pair(int(ch))
            elif '&' == ch:
                scr.addch(ch, color | style)
            elif '_' == ch:
                scr.addch(ch, color | style)
            elif '*' == ch:
                scr.addch(ch, color | style)

            control_mode = False
