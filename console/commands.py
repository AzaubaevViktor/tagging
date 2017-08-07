import itertools as it
from tag import SimpleEntry, LinkEntry


class BaseCommand:
    char = ""
    _about = ': [Help Create]'
    parent = None  # type: "Command"
    _args = ()

    def __init__(self):
        self.childrens = {}
        if self.parent is not None:
            self.parent.childrens[self.char] = self

    def __call__(self, stdscr, menu: "Menu", console: "Console", args):
        pass

    def about(self, *args):
        _args = {key: value or "" for key, value in it.zip_longest(self._args, args)}

        about = self._about

        _arg_s = []

        for key in self._args:
            value = _args[key]
            _arg_s.append("<{}{}>".format(
                key,
                ":" + value if value else value
            ))

        return about + " " + "; ".join(_arg_s)

base_cmd = BaseCommand()


class HelpCommand(BaseCommand):
    char = 'h'
    _about = 'This is Help'
    parent = base_cmd

HelpCommand()


class Create(BaseCommand):
    char = 'c'
    _about = "Create: [Entry]"
    parent = base_cmd

create = Create()


class CreateEntry(BaseCommand):
    char = 'e'
    _about = 'Create Entry: [Simple Link]'
    parent = create

create_entry = CreateEntry()


class CreateEntrySimple(BaseCommand):
    char = 's'
    _about = 'Create Entry Simple'
    parent = create_entry
    _args = ("name", "comment")

    def __call__(self, stdscr, menu: "Menu", console: "Console", args):
        entry = SimpleEntry(args[0], args[1])
        menu.manager.add_item_to_cur_tag(entry)
        menu.update_items()

CreateEntrySimple()


class CreateEntryLink(BaseCommand):
    char = 'l'
    _about = 'Create Entry Link'
    parent = create_entry

    _args = ("link", "comment")

    def __call__(self, stdscr, menu: "Menu", console: "Console", args):
        entry = LinkEntry(args[0], args[1])
        menu.manager.add_item_to_cur_tag(entry)
        menu.update_items()

CreateEntryLink()