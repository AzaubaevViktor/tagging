import abc
import webbrowser

import subprocess

from pathlib import Path


class AbstractItemType(metaclass=abc.ABCMeta):
    _header_fmt = ""
    _header_low_fmt = ""
    _about_fmt = ""

    def _tags(self):
        from tag import AbstractEntry

        if hasattr(self, 'source') and isinstance(self.source, AbstractEntry):
            entry = self.source
            tags_list = [tag.name for tag in entry.tags]
            return tags_list

    def press(self):
        pass

    @property
    def header_low(self) -> str:
        return self._header_low_fmt.format(**self.__dict__)

    @property
    def header(self) -> str:
        return self._header_fmt.format(**self.__dict__)

    @property
    def about(self) -> str:
        return self._about_fmt.format(**self.__dict__)


class SimpleItem(AbstractItemType):
    _header_fmt = "{name}"
    _about_fmt = "{comment}"

    def __init__(self,
                 source,
                 name: str,
                 comment: str
                 ):
        self.source = source
        self.name = name
        self.comment = comment
        self.tags = self._tags()

    def press(self):
        pass


class LinkItem(AbstractItemType):
    _header_fmt = "{name}"
    _header_low_fmt = "{link}"
    _about_fmt = "{comment}"

    def __init__(
            self,
            source,
            name: str,
            comment: str,
            link: str
    ):
        self.source = source
        self.name = name
        self.comment = comment
        self.link = link
        self.tags = self._tags()

    def press(self):
        webbrowser.open(self.link)


class FileItem(AbstractItemType):
    _header_fmt = "{name}"
    _header_low_fmt = "({path})"
    _about_fmt = "{comment}"

    def __init__(
            self,
            source,
            name: str,
            comment: str,
            path: str
    ):
        self.source = source
        self.name = name
        self.comment = comment
        self.path = path.replace("~", str(Path.home()))
        self.tags = self._tags()

    def press(self):
        subprocess.run(['xdg-open', self.path])


class TagItem(AbstractItemType):
    _header_fmt = "{name}"
    _about_fmt = "{entries_count} entries, {tags_count} tags"

    def __init__(
            self,
            source: "Tag",
            tag_manager: "TagManager"
    ):
        self.source = source  # type: "Tag"
        self.name = source.name
        self.comment = "Tag"
        self.manager = tag_manager
        self.entries_count = len(self.source.entries)
        self.tags_count = len(self.source.children)

    def press(self):
        self.manager.active_tag = self.source
