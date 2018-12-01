# cluegen.py
# 
# Classes generated from type clues.
#
# Author: David Beazley (@dabeaz). http://www.dabeaz.com

__all__ = ['Init', 'Repr', 'Equals']

def cluegen(func):
    def __get__(self, instance, cls):
        locs = { }
        exec(func(cls), locs)
        setattr(cls, func.__name__, locs[func.__name__])
        return getattr(cls, func.__name__).__get__(instance, cls)
    return type('D', (), { '__get__': __get__})()

class Init:
    @cluegen
    def __init__(cls):
        args = ', '.join('%s=%r' % (name, getattr(cls, name))
                        if hasattr(cls, name) else name
                        for name in cls.__annotations__)
        body = '\n'.join('  self.%s = %s' % (name,name) 
                         for name in cls.__annotations__)
        return 'def __init__(self, %s):\n%s\n' % (args, body)

class Repr:
    @cluegen
    def __repr__(cls):
        vals = ','.join('self.%s' % name for name in cls.__annotations__)
        fmt = ', '.join('%s=%%r' % name for name in cls.__annotations__)
        return 'def __repr__(self):\n' \
               '    return "%s(%s)" %% (%s)\n' % (cls.__name__, fmt, vals)

class Equals:
    @cluegen
    def __eq__(cls):
        selfvals = ','.join('self.%s' % name for name in cls.__annotations__)
        othervals = ','.join('other.%s' % name for name in cls.__annotations__)
        return 'def __eq__(self, other):\n' \
               '    if self.__class__ is other.__class__:\n' \
               '        return (%s,) == (%s,)\n' \
               '    else:\n' \
               '        return NotImplemented\n' % (selfvals, othervals)

# EXAMPLE USE
if __name__ == '__main__':
    # Pick the features that you want in a base class
    class Base(Init, Repr):
        pass

    # Start defining class
    class Coordinates(Base):
        x: int
        y: int

    class Stock(Base):
        name: str
        shares: int
        price: float

    class Vec3(Base):
        x: float
        y: float
        z: float

