import curses

from curses_wrapper import colors

from .commands import base_cmd


class Console:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.win = curses.newwin(3, self.width, self.height - 3, 0)
        self.line = ""
        self.a = 0
        self.menu = None  # type: "Menu"

    def key_handle(self, key):

        if isinstance(key, str):
            if "\n" == key:
                self.run()
                self.line = ""
            else:
                self.line += key
        else:
            if curses.KEY_BACKSPACE == key:
                self.line = self.line[:-1]

    @property
    def args(self):
        pos = self.line.find(" ")
        if -1 == pos:
            return tuple()

        args = self.line[pos:]
        return [x.strip() for x in args.split(";")]

    @property
    def cmd(self):
        cmd = base_cmd
        for ch in self.line:
            if ' ' == ch:
                break
            cmd = cmd.childrens.get(ch, None)
            if not cmd:
                break

        return cmd

    def get_help(self):
        cmd = self.cmd

        if not cmd:
            hlp = "Unknown command. Enter `h` for help"
        else:
            hlp = cmd.about(*self.args)

        return hlp

    def render(self):
        self.a += 1
        line = "> " + self.line

        self.win.clear()
        self.win.addstr(0, 0, "=" * self.width)
        self.win.addstr(1, 0, line, colors.TEXT)
        self.win.addstr(2, 0, self.get_help(), colors.COMMENT)

    def run(self):
        cmd = self.cmd

        if not cmd:
            return False
        else:
            cmd(self.stdscr, self.menu, self, self.args)
            return True

    def refresh(self):
        self.win.refresh()
