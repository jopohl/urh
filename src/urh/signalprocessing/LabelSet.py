import random
import string

from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.util.Logger import logger


class LabelSet(list):
    def __init__(self, name: str, iterable=None, id=None):
        iterable = iterable if iterable else []
        super().__init__(iterable)

        self.name = name
        self.__id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50)) if id is None else id


    def get_label_range(self):
        pass # TODO

    def convert_index(self):
        pass # todo

    @property
    def id(self) -> str:
        return self.id

    def append(self, lbl: ProtocolLabel):
        super().append(lbl)

    def remove(self, lbl: ProtocolLabel):
        if lbl in self:
            super().remove(lbl)
        else:
            logger.warning(lbl.name + " is not in set, so cant be removed")

    def __getitem__(self, index) -> ProtocolLabel:
        return super().__getitem__(index)