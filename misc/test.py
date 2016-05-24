from copy import deepcopy

from PyQt5.QtCore import QObject, pyqtSignal


class Sender(QObject):
    signal = pyqtSignal(str)

    def __init__(self, str):
        super().__init__()
        self.a = str

    def emit_signal(self):
        self.signal.emit(self.a)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        result.signal = self.signal
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        #result.signals = LabelSignals()
        return result

def print1(str):
    print("1 ", str)

def print2(str):
    print("2 ", str)


o1 = Sender("o1")
o2 = Sender("o2")

o1c = deepcopy(o1)

o1.signal.connect(print1)
o2.signal.connect(print2)

o1c.emit_signal()
o2.emit_signal()