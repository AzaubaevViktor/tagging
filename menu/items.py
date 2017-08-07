import abc
import webbrowser

import subprocess

from pathlib import Path


class AbstractItemType(metaclass=abc.ABCMeta):
    def press(self):
        pass


class SimpleItem(AbstractItemType):
    def __init__(self,
                 source,
                 name: str,
                 comment: str
                 ):
        self.source = source
        self.name = name
        self.comment = comment

    def press(self):
        pass


class LinkItem(AbstractItemType):
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

    def press(self):
        webbrowser.open(self.link)


class FileItem(AbstractItemType):
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

    def press(self):
        subprocess.run(['xdg-open', self.path])


class TagItem(AbstractItemType):
    def __init__(
            self,
            source: "Tag",
            tag_manager: "TagManager"
    ):
        self.source = source
        self.name = source.name
        self.comment = "Tag"
        self.manager = tag_manager

    def press(self):
        self.manager.active_tag = self.source
