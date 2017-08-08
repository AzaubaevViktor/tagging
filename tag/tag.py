from typing import Set

import anytree

from menu import TagItem


class Tag(anytree.NodeMixin):
    separator = " > "
    fields = ('name', )

    def __init__(self, name, parent=None):
        super().__init__()
        self.name = name
        self._entries = set()  # type: Set[SimpleEntry]
        self.parent = parent
        self._manager = None

    @property
    def manager(self):
        return self.root._manager

    @property
    def entries(self) -> Set['SimpleEntry']:
        return self._entries

    def add_entry(self, entry: "SimpleEntry"):
        if entry not in self._entries:
            self._entries.add(entry)
            entry.add_tag(self)

    def remove_entry(self, entry: "SimpleEntry"):
        if entry in self.entries:
            self._entries.remove(entry)
            entry.remove_tag(self)

    @property
    def item(self):
        return TagItem(self, self.manager)

    def __json__(self):
        return {
            "id": id(self),
            "name": self.name,
            "parent": id(self.parent) if self.parent is not None else -1
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Tag `{}`>".format(self.separator.join(
            [tag.name for tag in self.path]
        ))
