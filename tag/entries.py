import abc
from typing import List

import lxml.html

from menu import AbstractItemType, SimpleItem, LinkItem, FileItem
from .tag import Tag

_classes = {}


class AbstractEntry(metaclass=abc.ABCMeta):
    fields = ()

    @abc.abstractmethod
    def __init__(self, name):
        self.id = None
        self.name = name
        self._tags = set()

    @property
    def tags(self):
        return self._tags

    def add_tag(self, tag: Tag):
        if tag not in self._tags:
            self._tags.add(tag)
            tag.add_entry(self)

    def add_tags(self, tags: List[Tag]):
        for tag in tags:
            self.add_tag(tag)

    def remove_tag(self, tag: Tag):
        if tag in self.tags:
            self._tags.remove(tag)
            tag.remove_entry(self)

    def __json__(self):
        data = {
            "id": self.id,
            "tags": [tag.id for tag in self.tags],
            "class": self.__class__.__name__
        }

        for field in self.fields:
            data[field] = getattr(self, field)

        return data

    @classmethod
    def __from_json__(cls, manager, data):
        cls = _classes[data['class']]

        kwargs = {k: data.get(k, "") for k in cls.fields}
        kwargs['tags'] = [manager.get_by_id(_id) for _id in data['tags']]
        entry = cls(**kwargs)
        entry.id = data['id']
        return entry

    @classmethod
    def register(cls):
        _classes[cls.__name__] = cls


class SimpleEntry(AbstractEntry):
    fields = ('name', 'comment')

    def __init__(self, name: str, comment: str, tags: List[Tag] = None):
        self.name = name
        self.comment = comment
        self._tags = set()
        self.add_tags(tags or [])

    @property
    def item(self) -> AbstractItemType:
        return SimpleItem(self, self.name, self.comment)

SimpleEntry.register()


class LinkEntry(SimpleEntry):
    fields = ('name', 'link', 'comment')

    def __init__(self, link: str, comment: str, tags: List[Tag] = None, name=""):
        self._link = ""
        self.name = name
        self.link = link

        super().__init__(self.name, comment, tags)

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, val):
        val = str(val)
        if ("http://" not in val) and ("https://" not in val):
            val = "http://" + val

        if not self.name:
            try:
                t = lxml.html.parse(val)
                self.name = t.find(".//title").text.strip()
            except Exception:
                self.name = val

        self._link = val

    @property
    def item(self) -> AbstractItemType:
        return LinkItem(self, self.name, self.comment, self.link)

LinkEntry.register()


class FileEntry(SimpleEntry):
    fields = ('path', 'comment')

    def __init__(self, path: str, comment: str, tags: List[Tag] = None):
        self._path = ""
        self.path = path
        super().__init__(self.name, comment, tags)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if len(path) != 1 and path[-1] == '/':
            path = path[-1]

        self._path = path
        self.name = path.split("/")[-1]

    @property
    def item(self) -> AbstractItemType:
        return FileItem(self, self.name, self.comment, self.path)

FileEntry.register()
