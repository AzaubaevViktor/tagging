import abc


class AbstractItemType(metaclass=abc.ABCMeta):
    def press(self):
        pass


class SimpleItem:
    def __init__(self,
                 name: str,
                 comment: str
                 ):
        self.name = name
        self.comment = comment
