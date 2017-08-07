from typing import List
import anytree

from menu import SimpleItem, TagItem


class TagManager:
    def __init__(self):
        self.root_tag = Tag(0, "")
        self.root_tag._manager = self

        t1 = Tag(1, "FirstTag", parent=self.root_tag)
        t2 = Tag(2, "SecondTag", parent=self.root_tag)
        t11 = Tag(3, "InsideTag", parent=t1)

        self.entries = [
            Entry(1, "First Text", "Comment1 bI, root_tag", [self.root_tag]),
            Entry(2, "Second Text", "Comment1 bI, t1", [t1]),
            Entry(3, "Third Text", "Comment1 bI, t2", [t2]),
            Entry(4, "Fourth Text", "Comment1 bI, t11", [t11]),
            Entry(5, "Fifth Text", "Comment1 bI, t1, t2", [t1, t2]),
            Entry(6, "Sixth Text", "Comment1 bI, t2, t11", [t2, t11]),
        ]

        self.active_tag = self.root_tag

    @property
    def items(self):
        items = []
        for tag in self.active_tag.children:
            items.append(tag.item)

        for entry in self.active_tag.entries:
            items.append(entry.item)

        return items


class Tag(anytree.NodeMixin):
    separator = " > "

    def __init__(self, _id, name, parent=None):
        super().__init__()
        self._id = _id
        self.name = name
        self._entries = set()
        self.parent = parent
        self._manager = None

    @property
    def manager(self):
        return self.root._manager

    @property
    def entries(self):
        return self._entries

    def add_entry(self, entry: "Entry"):
        if entry not in self._entries:
            self._entries.add(entry)
            entry.add_tag(self)

    @property
    def item(self):
        return TagItem(self, self.manager)




class Entry:
    def __init__(self, _id: int, name: str, comment: str, tags: List[Tag]):
        self._id = _id
        self.name = name
        self.comment = comment
        self._tags = set()
        self.add_tags(tags)

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

    @property
    def item(self):
        return SimpleItem(self.name, self.comment)

