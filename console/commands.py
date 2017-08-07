
class BaseCommand:
    char = ""
    _about = 'Enter `h` for Help'
    parent = None  # type: "Command"

    def __init__(self):
        self.childrens = {}
        if self.parent is not None:
            self.parent.childrens[self.char] = self

    def run(self, stdscr, menu: "Menu", console: "Console"):
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
    _about = "Create: Item"
    parent = base_cmd

create = Create()


class CreateItem(BaseCommand):
    char = 'i'
    _about = 'Create Item "<name>" "<comment>"'
    parent = create

    def about(self, name="", comment=""):
        return self._about.replace(
            "<name>",
            "<name:{}>".format(name)
        ).replace(
            "<comment>",
            "<comment:{}>".format(comment)
        )

CreateItem()
