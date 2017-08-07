from menu import SimpleItem
from tag import SimpleEntry, LinkEntry


class BaseCommand:
    char = ""
    _about = ': [Help Create]'
    parent = None  # type: "Command"

    def __init__(self):
        self.childrens = {}
        if self.parent is not None:
            self.parent.childrens[self.char] = self

    def __call__(self, stdscr, menu: "Menu", console: "Console", args):
        pass

    def about(self, *args):
        return self._about

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
    _about = 'Create Entry Simple <name>; <comment>'
    parent = create_entry

    def about(self, name="", comment=""):
        return self._about.replace(
            "<name>",
            "<name:{}>".format(name)
        ).replace(
            "<comment>",
            "<comment:{}>".format(comment)
        )

    def __call__(self, stdscr, menu: "Menu", console: "Console", args):
        entry = SimpleEntry(args[0], args[1])
        menu.manager.add_item_to_cur_tag(entry)
        menu.update_items()

CreateEntrySimple()


class CreateEntryLink(BaseCommand):
    char = 'l'
    _about = 'Create Entry Link <link>; <comment>'
    parent = create_entry

    def about(self, link="", comment=""):
        return self._about.replace(
            "<link>",
            "<link:{}>".format(link)
        ).replace(
            "<comment>",
            "<comment:{}>".format(comment)
        )

    def __call__(self, stdscr, menu: "Menu", console: "Console", args):
        entry = LinkEntry(args[0], args[1])
        menu.manager.add_item_to_cur_tag(entry)
        menu.update_items()

CreateEntryLink()