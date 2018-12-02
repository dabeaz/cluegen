import cluegen

class Base(cluegen.Init, cluegen.Repr):
    pass

class Coordinates(Base):
    x: int
    y: int

class Coordinates3(Coordinates):
    z: int

class Holding(Base):
    name: str
    shares: int
    price: float


