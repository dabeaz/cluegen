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

from cluegen import all_clues
class Mytum(Datum):
    @cluegen
    def as_dict(cls):
        clues = all_clues(cls)
        return ('def as_dict(self):\n' + 
                '    return {\n' +
                '\n'.join(f'   {key!r}: self.{key},\n' for key in clues) +
                '}\n')

class Point(Mytum):
    x: int
    y: int

# An example of generating code from slots instead

from cluegen import DatumBase

def all_slots(cls):
    slots = []
    for cls in cls.__mro__:
        slots[0:0] = getattr(cls, '__slots__', [])
    return slots

class Slotum(DatumBase):
    __slots__ = ()

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.__match_args__ = tuple(all_slots(cls))
    
    @cluegen
    def __init__(cls):
        slots = all_slots(cls)
        return ('def __init__(self, ' + ','.join(slots) + '):\n' +
                '\n'.join(f'    self.{name} = {name}' for name in slots)
                )

    @cluegen
    def __repr__(cls):
        slots = all_slots(cls)
        return ('def __repr__(self):\n' + 
                f'    return f"{cls.__name__}(' + 
                ','.join('%s={self.%s!r}' % (name, name) for name in slots) + ')"'
                )

class Fraction(Slotum):
    __slots__ = ('numer', 'denom')



                   

               

