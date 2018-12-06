# cluegen.py
# 
# Classes generated from type clues. 
#
# Author: David Beazley (@dabeaz). 
#         http://www.dabeaz.com
#
# Copyright (C) 2018.
#
# Permission is granted to use, copy, and modify this code in any
# manner as long as this copyright message and disclaimer remain in
# the source code.  There is no warranty.  Try to use the code for the
# greater good.
#
# Take a course! https://www.dabeaz.com/courses.html


def all_clues(cls):
    clues = { }
    for c in reversed(cls.__mro__):
        clues.update(getattr(c, '__annotations__', {}))
    return clues

def cluegen(func):
    def __get__(self, instance, cls):
        clues = all_clues(cls)
        if clues:
            locs = { }
            code = func(cls, clues)
            exec(code, locs)
            meth = locs[func.__name__]
            setattr(cls, func.__name__, meth)
            return meth.__get__(instance, cls)
        else:
            return self
    return type(f'ClueGen_{func.__name__}', (), dict(__get__=__get__))()

class Init:
    @cluegen
    def __init__(cls, clues):
        args = ', '.join(f'{name}={getattr(cls,name)!r}'
                        if hasattr(cls, name) else name
                        for name in clues)
        body = '\n'.join(f'  self.{name} = {name}'
                         for name in clues)
        return f'def __init__(self, {args}):\n{body}\n'

    # This method is needed if you want to propagate the method via inheritance.
    # Child classes need to make sure they can lazily produce the correct method.
    # So, we copy the magic code generation descriptor from here to the child.
    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        cls.__init__ = Init.__init__
        super().__init_subclass__(*args, **kwargs)

class Repr:
    @cluegen
    def __repr__(cls, clues):
        fmt = ', '.join('%s={self.%s!r}' % (name, name) for name in clues)
        return 'def __repr__(self):\n' \
               '    return f"{type(self).__name__}(%s)"' % fmt

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        cls.__repr__ = Repr.__repr__
        super().__init_subclass__(*args, **kwargs)

class Iter:
    @cluegen
    def __iter__(cls, clues):
        values = '\n'.join(f'    yield self.{name}' for name in clues)
        return 'def __iter__(self):\n' + values

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        cls.__iter__ = Iter.__iter__
        super().__init_subclass__(*args, **kwargs)

class Eq:
    @cluegen
    def __eq__(cls, clues):
        selfvals = ','.join(f'self.{name}' for name in clues)
        othervals = ','.join(f'other.{name}'for name in clues)
        return 'def __eq__(self, other):\n' \
               '    if self.__class__ is other.__class__:\n' \
               f'        return ({selfvals},) == ({othervals},)\n' \
               '    else:\n' \
               '        return NotImplemented\n'

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        cls.__eq__ = Eq.__eq__
        super().__init_subclass__(*args, **kwargs)

# EXAMPLE USE
if __name__ == '__main__':
    # Pick the features that you want in a base class
    class Base(Init, Repr, Eq, Iter):
        pass

    # Start defining classes
    class Coordinates(Base):
        x: int
        y: int


