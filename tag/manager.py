import json
import shutil

from anytree import LevelOrderIter

from settings import FILE_DB
from .entries import SimpleEntry, LinkEntry, AbstractEntry
from .tag import Tag


class TagManager:
    def __init__(self):
        self.root_tag = Tag("")
        self.root_tag._manager = self

        t1 = Tag("FirstTag", parent=self.root_tag)
        t2 = Tag("SecondTag", parent=self.root_tag)
        t11 = Tag("InsideTag", parent=t1)

        self.entries = [
            SimpleEntry("First Text", "Comment1 bI, root_tag", [self.root_tag]),
            SimpleEntry("Second Text", "Comment1 bI, t1", [t1]),
            SimpleEntry("Third Text", "Comment1 bI, t2", [t2]),
            SimpleEntry("Fourth Text", "Comment1 bI, t11", [t11]),
            SimpleEntry("Fifth Text", "Comment1 bI, t1, t2", [t1, t2]),
            SimpleEntry("Sixth Text", "Comment1 bI, t2, t11", [t2, t11]),
            LinkEntry("http://google.ru", "comment", [t1])
        ]

        self.active_tag = self.root_tag

    def up(self):
        self.active_tag = self.active_tag.parent or self.root_tag

    @property
    def items(self):
        items = []
        for tag in self.active_tag.children:
            items.append(tag.item)

        for entry in self.active_tag.entries:
            items.append(entry.item)

        return items

    def get_tag(self, name: str):
        for tag in LevelOrderIter(self.root_tag, filter_=lambda n: bool(n.name)):
            if name == tag.name:
                return tag

        return None

    @property
    def path(self):
        tag = self.active_tag
        return tag.separator.join([str(node.name) for node in tag.path]) or tag.separator

    def add_item_to_cur_tag(self, item):
        if isinstance(item, AbstractEntry):
            item.add_tag(self.active_tag)
        if isinstance(item, Tag):
            item.parent = self.active_tag

    def delete_item(self, item):
        if isinstance(item, Tag):
            item.parent = None
            for child in item.children:
                self.delete_item(child)
            for entry in item.entries:
                entry.remove_tag(item)
        elif isinstance(item, AbstractEntry):
            for tag in item.tags:
                tag.remove_entry(item)

    def __json__(self):
        return {
            "tags": [tag.__json__() for tag in LevelOrderIter(self.root_tag)],
            "entries": [entry.__json__() for entry in self.entries]
        }

    def save(self):
        try:
            shutil.copyfile(FILE_DB, ".{}.backup".format(FILE_DB))
        except FileNotFoundError:
            pass
        json.dump(self.__json__(), open(FILE_DB, "wt"), indent=4)

