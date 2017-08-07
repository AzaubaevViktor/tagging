import curses
import curses.ascii
from curses.textpad import Textbox


class MyTextPad(Textbox):
    def __init__(self, win, default):
        super().__init__(win)

        self.default = default
        self.line = default
        self._pos = len(default)
        self.refresh()

        self.just_started = True

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, val):
        self._pos = val
        if self._pos < 0:
            self._pos = 0
        if self._pos > len(self.line):
            self._pos = len(self.line)

    @property
    def cursor_pos(self):
        y = self.pos // self.maxx
        x = self.pos % self.maxx

        return y, x

    def refresh(self):
        self.win.clear()
        for y in range(self.maxy):
            self.win.addstr(y, 0, self.line[self.maxx * y:self.maxx * (y + 1)])
        self.win.move(*self.cursor_pos)
        self.win.refresh()

    def do_command(self, ch):
        ordch = ord(ch) if isinstance(ch, str) else ch
        ch = chr(ch) if isinstance(ch, int) else ch

        if curses.KEY_BACKSPACE == ordch:
            self.line = self.line[:self.pos -1] + self.line[self.pos:]
            self.pos -= 1
        elif curses.KEY_LEFT == ordch:
            self.pos -= 1
        elif curses.KEY_RIGHT == ordch:
            self.pos += 1
        elif curses.KEY_DOWN == ordch:
            self.pos += self.maxx
        elif curses.KEY_DC == ordch:
            self.line = self.line[:self.pos] + self.line[self.pos + 1:]
        elif curses.KEY_UP == ordch:
            self.pos -= self.maxx
        elif '\n' == ch:
            if not self.just_started:
                return 0
        elif 27 == ordch:
            return -1
        elif ch.isprintable():
            self.line = self.line[:self.pos] + ch + self.line[self.pos:]
            self.pos += 1

        self.just_started = False
        return True

    def gather(self):
        return self.line.strip()

    def edit(self, validate=None):
        while 1:
            ch = self.win.get_wch()

            if validate:
                ch = validate(ch)

            if not ch:
                continue

            code = self.do_command(ch)

            if code == -1:
                return self.default

            if not code:
                break

            self.refresh()
        return self.gather()
