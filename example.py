import cluegen

class Base(cluegen.ClueGen):
    __slots__ = ()
    __init__ = cluegen.__init__
    __repr__ = cluegen.__repr__

class Coordinates(Base):
    x: int
    y: int

class Coordinates3(Coordinates):
    z: int

class Holding(Base):
    name: str
    shares: int
    price: float


