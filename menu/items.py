import abc
import webbrowser

import subprocess

from pathlib import Path


class AbstractItemType(metaclass=abc.ABCMeta):
    def press(self):
        pass


class SimpleItem(AbstractItemType):
    def __init__(self,
                 name: str,
                 comment: str
                 ):
        self.name = name
        self.comment = comment


class LinkItem(AbstractItemType):
    def __init__(
            self,
            name: str,
            comment: str,
            link: str
    ):
        self.name = name
        self.comment = comment
        self.link = link

    def press(self):
        webbrowser.open(self.link)


class FileItem(AbstractItemType):
    def __init__(
            self,
            name: str,
            comment: str,
            address: str
    ):
        self.name = name
        self.comment = comment
        self.address = address.replace("~", str(Path.home()))

    def press(self):
        subprocess.run(['xdg-open', self.address])
