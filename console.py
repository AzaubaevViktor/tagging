import abc
import curses

from curses_wrapper import colors


class BaseCommand:
    def __init__(self, char, about, parent: "Command"):
        self.char = char
        self.about = about
        self.parent = parent
        self.childrens = {}
        if parent is not None:
            self.parent.childrens[self.char] = self

    def run(self, stdscr, menu: "Menu", console: "Console"):
        pass

base_cmd = BaseCommand('', 'Enter `h` for Help', None)


class HelpCommand(BaseCommand):
    pass

HelpCommand('h', 'This is help!', base_cmd)


class Console:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.win = curses.newwin(2, self.width, self.height - 5, 0)
        self.line = "хуй"
        self.a = 0

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

    def get_help(self):
        cmd = base_cmd
        hlp = base_cmd.about
        for ch in self.line:
            child = cmd.childrens.get(ch, None)
            cmd = child
            if not cmd:
                break

        if not cmd:
            hlp = "Unknown command. Enter `h` for help"
        else:
            hlp = cmd.about

        return hlp

    def render(self):
        self.a += 1
        line = "> " + self.line

        self.win.clear()
        self.win.addstr(0, 0, "=" * self.width)
        self.win.addstr(1, 0, "> " + self.line, colors.TEXT)
        self.win.addstr(1, len(line) + 1, self.get_help(), colors.COMMENT)

    def run(self):
        pass

    def refresh(self):
        self.win.refresh()
