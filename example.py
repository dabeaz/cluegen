from cluegen import Datum, cluegen

class Coordinates(Datum):
    x: int
    y: int

class Coordinates3(Coordinates):
    z: int

class Holding(Datum):
    name: str
    shares: int
    price: float

# Example of extending Datum with a new feature

class MyDatum(Datum):
    @cluegen
    def as_dict(cls, clues):
        return ('def as_dict(self):\n' + 
                '    return {\n' +
                '\n'.join(f'   {key!r}: self.{key},\n' for key in clues) +
                '}\n')

class Point(MyDatum):
    x: int
    y: int


               

