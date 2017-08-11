import json
import shutil
from random import randint
from typing import List

from anytree import LevelOrderIter

from settings import FILE_DB
from .entries import AbstractEntry
from .tag import Tag
from copy import copy


class TagManager:
    def __init__(self):
        self.root_tag = Tag("Root", _id=Tag.ROOT_ID)
        self.root_tag._manager = self

        self.entries = []  # type: List[AbstractEntry]

        self.active_tag = self.root_tag

        self.ids = {0: self.root_tag}

    def get_id(self, who) -> int:
        ids = set()

        for tag in LevelOrderIter(self.root_tag):
            if hasattr(tag, 'id'):
                ids.add(tag.id)

        for entry in self.entries:
            ids.add(entry.id)

        _id = id(who)
        while _id in ids:
            _id = randint(1000000000)
        return _id

    def up(self):
        self.active_tag = self.active_tag.parent or self.root_tag

    def get_by_id(self, _id: int) -> Tag or AbstractEntry or None:
        for tag in LevelOrderIter(self.root_tag):
            if tag.id == _id:
                return tag

        for entry in self.entries:
            if entry.id == _id:
                return entry

        return None

    @property
    def items(self) -> List[Tag or AbstractEntry]:
        items = []
        for tag in self.active_tag.children:
            items.append(tag.item)
        for entry in self.active_tag.entries:
            items.append(entry.item)

        return items

    def get_tag(self, name: str) -> Tag or None:
        for tag in LevelOrderIter(self.root_tag, filter_=lambda n: bool(n.name)):
            if name == tag.name:
                return tag

        return None

    @property
    def path(self) -> str:
        tag = self.active_tag
        return tag.separator.join([str(node.name) for node in tag.path]) or tag.separator

    def add_item_to_cur_tag(self, item: Tag or AbstractEntry):
        item.id = self.get_id(item)

        if isinstance(item, AbstractEntry):
            item.add_tag(self.active_tag)
            self.entries.append(item)
        if isinstance(item, Tag):
            item.parent = self.active_tag

    def delete_item(self, item: Tag or AbstractEntry):
        if isinstance(item, Tag):
            item.parent = None
            for child in copy(item.children):
                self.delete_item(child)
            for entry in copy(item.entries):
                entry.remove_tag(item)
        elif isinstance(item, AbstractEntry):
            for tag in copy(item.tags):
                tag.remove_entry(item)

    def __json__(self):
        return {
            "tags": [tag.__json__() for tag in LevelOrderIter(self.root_tag)],
            "entries": [entry.__json__() for entry in self.entries]
        }

    def __from_json__(self, data: dict):
        for tag_data in data['tags']:
            tag = Tag.__from_json__(self, tag_data)
            if tag.id == -1:
                self.root_tag = tag
                self.active_tag = self.root_tag
                tag._manager = self

        for entry_data in data['entries']:
            if entry_data['tags']:
                self.entries.append(AbstractEntry.__from_json__(self, entry_data))

    def save(self):
        try:
            shutil.copyfile(FILE_DB, ".{}.backup".format(FILE_DB))
        except FileNotFoundError:
            pass
        f = open(FILE_DB, "wt")
        json.dump(self.__json__(), open(FILE_DB, "wt"), indent=4)
        f.close()
