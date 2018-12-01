from cluegen import Init, Repr

class Base(Init, Repr):
    pass

class Coordinates(Base):
    x: int
    y: int

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f'{type(self).__name__}(x={self.x!r}, y={self.y!r})'

class Holding(Base):
    name: str
    shares: int
    price: float

