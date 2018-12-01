from cluegen import Init, Repr

class Base(Init, Repr):
    pass

class Coordinates(Base):
    x: int
    y: int

class Holding(Base):
    name: str
    shares: int
    price: float

