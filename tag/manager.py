from typing import List, Set
import anytree

from menu import SimpleItem, TagItem, LinkItem, AbstractItemType, FileItem


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

    @property
    def path(self):
        tag = self.active_tag
        return tag.separator.join([str(node.name) for node in tag.path]) or tag.separator

    def add_item_to_cur_tag(self, item):
        if isinstance(item, SimpleEntry):
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


class Tag(anytree.NodeMixin):
    separator = " > "
    fields = ('name', )

    def __init__(self, name, parent=None):
        super().__init__()
        self.name = name
        self._entries = set() # type: Set[SimpleEntry]
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

    @property
    def item(self):
        return TagItem(self, self.manager)


class SimpleEntry:
    fields = ('name', 'comment')

    def __init__(self, name: str, comment: str, tags: List[Tag] = None):
        self.name = name
        self.comment = comment
        self._tags = set()
        self.add_tags(tags or [])

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
        self._tags.remove(tag)

    @property
    def item(self) -> AbstractItemType:
        return SimpleItem(self, self.name, self.comment)


class LinkEntry(SimpleEntry):
    fields = ('link', 'comment')

    def __init__(self, link: str, comment: str, tags: List[Tag] = None):
        self.link = link
        if "http://" not in self.link:
            self.link = "http://" + self.link

        name = self.link
        super().__init__(name, comment, tags)

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

