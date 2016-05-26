import random
import string

from urh.signalprocessing.ProtocoLabel import ProtocolLabel


class LabelSet(list):
    def __init__(self, name: str, iterable=None, id=None):
        super().__init__(iterable)

        self.name = name
        self.__id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50)) if id is None else id

    @property
    def id(self) -> str:
        return self.id

    def append(self, lbl: ProtocolLabel):
        super().append(lbl)

    def __getitem__(self, index) -> ProtocolLabel:
        return super().__getitem__(index)