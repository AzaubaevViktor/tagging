import itertools as it
from tag import SimpleEntry, LinkEntry
from tag.manager import FileEntry, Tag


class BaseCommand:
    char = ""
    name = None
    _about = None
    parent = None  # type: "Command"
    _args = ()

    def __init__(self):
        if self.name:
            self.char = self.name[0].lower()

        self.childrens = {}
        if self.parent is not None:
            self.parent.childrens[self.char] = self

    def __call__(self, stdscr, menu: "Menu", console: "Console", args):
        pass

    def console_path(self):
        pre = []

        cmd = self
        while cmd is not None:
            pre.append(cmd.name or "")
            cmd = cmd.parent

        pre.reverse()

        pre = " ".join(pre)

        variantes = [cmd.name for cmd in self.childrens.values()]
        if not variantes:
            variantes = ""
        else:
            variantes = "[{}]".format(
                " ".join(variantes)
            )

        return pre + ": " + variantes

    def about(self, *args):
        _args = {key: value or "" for key, value in it.zip_longest(self._args, args)}

        about = self._about or self.console_path()

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
    name = 'Help'
    _about = 'This is Help String, writed in _about field'
    parent = base_cmd

HelpCommand()


class Item(BaseCommand):
    name = "Item"
    parent = base_cmd

item = Item()


class DeleteItem(Item):
    name = "Delete"
    parent = item
    _args = ('yes', )

    def __call__(self, stdscr, menu: "Menu", console: "Console", args):
        if "y" in args[0].lower():
            menu.delete_item()

DeleteItem()


class Create(BaseCommand):
    name = 'Create'
    parent = base_cmd

create = Create()


class CreateTag(Create):
    name = "Tag"
    parent = create

    _args = ("name", )

    def __call__(self, stdscr, menu: "Menu", console: "Console", args):
        tag = Tag(args[0])
        menu.add_item(tag)

CreateTag()


class CreateEntry(BaseCommand):
    name = 'Entry'
    parent = create

    entry_class = None

    def __call__(self, stdscr, menu: "Menu", console: "Console", args):
        if self.entry_class is None:
            return

        if len(args) == 0:
            return
        elif len(args) == 1:
            args = args[0], "Edit this comment"

        entry = self.entry_class(args[0], args[1])
        menu.add_item(entry)

create_entry = CreateEntry()


class CreateEntrySimple(CreateEntry):
    name = 'Simple'
    parent = create_entry
    _args = ("name", "comment")

    entry_class = SimpleEntry

CreateEntrySimple()


class CreateEntryLink(CreateEntry):
    name = 'Link'
    parent = create_entry

    _args = ("link", "comment")

    entry_class = LinkEntry

CreateEntryLink()


class CreateEntryFile(CreateEntry):
    name = 'File'
    parent = create_entry

    _args = ("path", "comment")

    entry_class = FileEntry

CreateEntryFile()