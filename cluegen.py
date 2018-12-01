# cluegen.py
# 
# Classes generated from type clues.
#
# Author: David Beazley (@dabeaz). 
#         http://www.dabeaz.com
#
# Copyright (C) 2018

__all__ = ['Init', 'Repr', 'Equals']

def cluegen(func):
    def __get__(self, instance, cls):
        locs = { }
#        print("CODE:", func(cls))
        exec(func(cls), locs)
        setattr(cls, func.__name__, locs[func.__name__])
        return getattr(cls, func.__name__).__get__(instance, cls)
    return type('D', (), dict(__get__=__get__))()

class Init:
    @cluegen
    def __init__(cls):
        args = ', '.join(f'{name}={getattr(cls,name)!r}'
                        if hasattr(cls, name) else name
                        for name in cls.__annotations__)
        body = '\n'.join(f'  self.{name} = {name}'
                         for name in cls.__annotations__)
        return f'def __init__(self, {args}):\n{body}\n'

class Repr:
    @cluegen
    def __repr__(cls):
        fmt = ', '.join('%s={self.%s!r}' % (name, name) for name in cls.__annotations__)
        return 'def __repr__(self):\n' \
               '    return f"{type(self).__name__}(%s)"' % fmt

class Equals:
    @cluegen
    def __eq__(cls):
        selfvals = ','.join(f'self.{name}' for name in cls.__annotations__)
        othervals = ','.join(f'other.{name}'for name in cls.__annotations__)
        return 'def __eq__(self, other):\n' \
               '    if self.__class__ is other.__class__:\n' \
               f'        return ({selfvals},) == ({othervals},)\n' \
               '    else:\n' \
               '        return NotImplemented\n'

# EXAMPLE USE
if __name__ == '__main__':
    # Pick the features that you want in a base class
    class Base(Init, Repr):
        pass

    # Start defining classes
    class Coordinates(Base):
        x: int
        y: int


