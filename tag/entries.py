import abc
from typing import List

import lxml.html

from menu import AbstractItemType, SimpleItem, LinkItem, FileItem
from .tag import Tag


class AbstractEntry(metaclass=abc.ABCMeta):
    fields = ()

    @abc.abstractmethod
    def __init__(self, name):
        self.name = name

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
            "id": id(self),
            "tags": [id(tag) for tag in self.tags],
            "class": self.__class__.__name__
        }

        for field in self.fields:
            data[field] = getattr(self, field)

        return data


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


class LinkEntry(SimpleEntry):
    fields = ('link', 'comment')

    def __init__(self, link: str, comment: str, tags: List[Tag] = None):
        self._link = ""
        self.link = link

        super().__init__(self.name, comment, tags)

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, val):
        val = str(val)
        if "http://" not in val:
            val = "http://" + val

        try:
            t = lxml.html.parse(val)
            self.name = t.find(".//title").text
        except Exception:
            self.name = val

        self._link = val

    @property
    def item(self) -> AbstractItemType:
        return LinkItem(self, self.name, self.comment, self.link)


class FileEntry(SimpleEntry):
    fields = ('path', 'comment')

    def __init__(self, path: str, comment: str, tags: List[Tag] = None):
        self.path = path
        super().__init__(path.split("/")[-1], comment, tags)

    @property
    def item(self) -> AbstractItemType:
        return FileItem(self, self.name, self.comment, self.path)
