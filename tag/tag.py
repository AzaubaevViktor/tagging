from typing import Set

import anytree

from menu import TagItem


class Tag(anytree.NodeMixin):
    separator = '/'
    fields = ('name', )
    ROOT_ID = -1

    def __init__(self, name, parent=None, _id=None):
        super().__init__()
        self.name = name
        self._entries = set()  # type: Set[SimpleEntry]
        self.parent = parent
        self._manager = None

        self.id = _id or (self.manager and self.manager.get_id(self))

    @property
    def manager(self) -> "TagManager":
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
    def item(self) -> TagItem:
        return TagItem(self, self.manager)

    def __json__(self):
        return {
            "id": self.id,
            "name": self.name,
            "parent": self.parent.id if self.parent is not None else 0
        }

    @classmethod
    def __from_json__(cls, manager: "TagManger", data: dict):
        parent_id = data['parent']
        parent = None if 0 == parent_id else manager.get_by_id(parent_id)
        return Tag(data['name'], parent, _id=data['id'])

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Tag `{}`>".format(self.separator.join(
            [tag.name for tag in self.path]
        ))
