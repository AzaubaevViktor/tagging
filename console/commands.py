import curses
import curses.ascii
import itertools as it
from curses.textpad import rectangle, Textbox

from anytree import LevelOrderIter

from .my_textpad import MyTextPad
from tag import SimpleEntry, LinkEntry
from tag import FileEntry, Tag


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

    def __call__(self, *args, **kwargs):
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

    def arguments(self, *args, **kwargs):
        return {key: value or "" for key, value in it.zip_longest(self._args, args)}

    def about(self, *args, **kwargs):
        argkv = self.arguments(*args, **kwargs)

        about = self._about or self.console_path()

        _arg_s = []

        for key in self._args:
            value = argkv[key]
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

    def tag_predict(self, tag_name, **kwargs) -> Tag:
        manager = kwargs['manager']

        for tag in LevelOrderIter(manager.root_tag, filter_=lambda n: bool(n.name)):
            if tag.name.startswith(tag_name):
                return tag

item = Item()


class ItemEdit(Item):
    name = "Edit"
    parent = item

    _args = ('field', )

    box_size = (0.8, 0.8)

    def arguments(self, *args, **kwargs):
        argkv = super().arguments(*args, **kwargs)
        field_value = argkv['field']
        menu = kwargs['menu']  # type: "Menu"
        entry = menu.active_item.source  # type: "SimpleEntry"

        for field_name in entry.fields:
            if field_name.startswith(field_value):
                argkv['field'] = field_name

        return argkv

    def __call__(self, *args, **kwargs):
        args = self.arguments(*args, **kwargs)
        field_name = args['field']
        menu = kwargs['menu']
        item = menu.active_item.source

        stdscr = kwargs['stdscr']

        my, mx = stdscr.getmaxyx()
        sy = int(my * self.box_size[0])
        sx = int(mx * self.box_size[1])

        starty = (my - sy) // 2
        startx = (mx - sx) // 2

        header = "Edit field `{}`:".format(field_name)

        stdscr.addstr(starty, startx + (sx - len(header)) // 2, header)

        editwin = curses.newwin(sy - 3, sx - 1, starty + 2, startx + 1)
        rectangle(stdscr, starty + 1, startx, starty + sy, startx + sx)
        stdscr.refresh()

        box = MyTextPad(editwin, getattr(item, field_name))

        # Let the user edit until Ctrl-G is struck.
        box.edit()

        # Get resulting contents
        message = box.gather()

        setattr(item, field_name, message)

        menu.update_items()

item_edit = ItemEdit()


class ItemEditParent(ItemEdit):
    name = "Parent"
    parent = item_edit
    _args = ('parent', )

    def arguments(self, *args, **kwargs):
        argkv = BaseCommand.arguments(self, *args, **kwargs)
        tag_name = argkv['parent']

        if tag_name:
            parent = self.tag_predict(tag_name, **kwargs)
            if parent:
                argkv['parent'] = parent.name
            else:
                argkv['parent'] = ""

        return argkv

    def __call__(self, *args, **kwargs):
        argkv = self.arguments(*args, **kwargs)
        parent_name = argkv['parent']
        tag = kwargs['tag']
        manager = kwargs['manager']
        menu = kwargs['menu']

        if tag:
            tag.parent = manager.get_tag(parent_name)
            menu.update_items()


ItemEditParent()


class ItemTag(Item):
    name = "Tag"
    parent = item

    def about(self, *args, **kwargs):
        entry = kwargs['entry']
        if entry:
            return super().about(*args, **kwargs)
        else:
            return "Don't use this with Tag"

item_tag = ItemTag()


class ItemTagAdd(ItemTag):
    name = "Add"
    parent = item_tag
    _args = ("tag", "parent")

    def arguments(self, *args, **kwargs):
        argkv = super().arguments(*args, **kwargs)

        tag = self.tag_predict(argkv['tag'], **kwargs)

        if tag:
            # Нашли тэг
            argkv['tag'] = tag.name
            argkv['parent'] = ""
        else:
            # Не нашли -- делаем подсказку для parent
            parent_name = argkv['parent']
            # Если туда что-то написано
            if parent_name:
                parent = self.tag_predict(parent_name, **kwargs)
                if parent:
                    argkv['parent'] = parent.name
                else:
                    argkv['parent'] = ""

        return argkv

    def __call__(self, *args, **kwargs):
        entry = kwargs['entry']
        if not entry:
            return

        argkv = self.arguments(*args, **kwargs)
        tag_name = argkv['tag']

        manager = kwargs['manager']
        menu = kwargs['menu']

        tag = manager.get_tag(tag_name)

        if not tag:
            tag = Tag(tag_name, parent=manager.get_tag(argkv['parent'] or None))

        entry.add_tag(tag)
        menu.update_items()

ItemTagAdd()


class ItemTagDelete(ItemTag):
    name = "Delete"
    parent = item_tag
    _args = ("tag", )

    def tag_predict(self, tag_name, **kwargs):
        entry = kwargs['entry']
        if not entry:
            return

        for tag in entry.tags:
            if tag.name.startswith(tag_name):
                return tag

        return None

    def arguments(self, *args, **kwargs):
        argkv = super().arguments(*args, **kwargs)
        entry = kwargs['entry']

        if entry:
            tag = self.tag_predict(argkv['tag'], **kwargs)

            if tag:
                argkv['tag'] = tag.name

        return argkv

    def __call__(self, *args, **kwargs):
        entry = kwargs['entry']
        if not entry:
            return

        argkv = self.arguments(*args, **kwargs)
        tag_name = argkv['tag']

        manager = kwargs['manager']
        menu = kwargs['menu']

        entry.remove_tag(manager.get_tag(tag_name))
        menu.update_items()

ItemTagDelete()


class ItemDelete(Item):
    name = "Delete"
    parent = item
    _args = ('yes', )

    def __call__(self, *args, **kwargs):
        menu = kwargs['menu']

        if "y" in args[0].lower():
            menu.delete_item()

ItemDelete()


class Create(BaseCommand):
    name = 'Create'
    parent = base_cmd

create = Create()


class CreateTag(Create):
    name = "Tag"
    parent = create

    _args = ("name", )

    def __call__(self, *args, **kwargs):
        menu = kwargs['menu']

        tag = Tag(args[0])
        menu.add_item(tag)

CreateTag()


class CreateEntry(BaseCommand):
    name = 'Entry'
    parent = create

    entry_class = None

    def __call__(self, *args, **kwargs):
        menu = kwargs['menu']

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