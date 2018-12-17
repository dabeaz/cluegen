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

import types

# Function to collect all type clues from a class, including all base
# classes.
def all_clues(cls):
    clues = { }
    for c in reversed(cls.__mro__):
        clues.update(getattr(c, '__annotations__', {}))
    return clues

# Base class for special code-generation descriptors. Used so that
# they can be easily detected when inspecting classes.
class ClueGenDescriptor:
    pass

# Decorator to define methods of a class as a code generator.
# Functions are passed the class and a list of type clues (including
# those collected from base classes)
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
    return type(f'{func.__name__}', (ClueGenDescriptor,), dict(__get__=__get__))()

# Base class for defining the "Base" code generator class.  This class
# watches subclasses, makes sure that they define __slots__ = (), and
# collects information needed to make an __init_subclass__ method that
# clones the code-generation descriptors.
class ClueGen:
    __slots__ = ()
    @classmethod
    def __init_subclass__(cls):
        if '__slots__' not in vars(cls):
            raise TypeError(f'{cls.__name__} must define __slots__ = ()')
        to_copy = [ (name, val) for name, val in vars(cls).items()
                   if isinstance(val, ClueGenDescriptor) ]

        @classmethod
        def __init_subclass__(cls):
            for name, val in to_copy:
                setattr(cls, name, val)
        cls.__init_subclass__ = __init_subclass__

# Various special methods that can be used in a base class.
@cluegen
def __init__(cls, clues):
    args = ', '.join(f'{name}={getattr(cls,name)!r}'
                    if hasattr(cls, name) and not isinstance(getattr(cls, name), types.MemberDescriptorType) else name
                    for name in clues)
    body = '\n'.join(f'  self.{name} = {name}'
                     for name in clues)
    return f'def __init__(self, {args}):\n{body}\n'

@cluegen
def __repr__(cls, clues):
    fmt = ', '.join('%s={self.%s!r}' % (name, name) for name in clues)
    return 'def __repr__(self):\n' \
           '    return f"{type(self).__name__}(%s)"' % fmt

@cluegen
def __iter__(cls, clues):
    values = '\n'.join(f'    yield self.{name}' for name in clues)
    return 'def __iter__(self):\n' + values


@cluegen
def __eq__(cls, clues):
    selfvals = ','.join(f'self.{name}' for name in clues)
    othervals = ','.join(f'other.{name}'for name in clues)
    return 'def __eq__(self, other):\n' \
           '    if self.__class__ is other.__class__:\n' \
           f'        return ({selfvals},) == ({othervals},)\n' \
           '    else:\n' \
           '        return NotImplemented\n'

# A default Base class
class DefaultBase(ClueGen):
    __slots__ = ()
    __init__ = __init__
    __repr__ = __repr__

# EXAMPLE USE
if __name__ == '__main__':
    # Start defining classes
    class Coordinates(DefaultBase):
        x: int
        y: int


