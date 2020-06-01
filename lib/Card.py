from lib.constants import VALUES, FACES
from collections import namedtuple


class Card(namedtuple('Card', ['face', 'value'])):
    __slots__ = ()

    def __init__(self, face=None, value=None):
        super().__init__()

    def __str__(self):
        return VALUES[self.value] + FACES[self.face]

    def __hash__(self):
        return self.value

    def value_equal(self, other):
        return self.value == other.value

    def face_equal(self, other):
        return self.face == other.face

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def to_dict(self):
        return {"face": self.face, "value": self.value}
