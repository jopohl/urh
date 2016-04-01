from PyQt5.QtCore import QObject


class A(QObject):
    def __init__(self):
        self.a = 1

    def __str__(self):
        return "a"

    def __repr__(self):
        return "a"


l = []
for _ in range(10):
    l.append(A())

print(l)
l2 = l
del l[-1]
print(l)
print(l2)
