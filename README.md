# cluegen - Classes From Type Clues

Cluegen is a library that makes it easy for you to define classes using
Python type clues. Here how it works. First, you pick the features that you
want and you put them in a base class:

    from cluegen import Init, Repr

    class Base(Init, Repr):
        pass

In this example, `Base` provides an `__init__()` and a
`__repr__()` method for you. Next, you simply start defining your 
classes via inheritance:

    class Coordinates(Base):
        x: int
        y: int

The resulting class works exactly as you want:

    >>> a = Coordinates(2, 3)
    >>> a
    Coordinates(x=2, y=3)
    >>> a.x
    2
    >>> a.y
    3
    >>> 

And the performance is the same as defining classes by hand.
For example, suppose you had this class:

    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __repr__(self):
            return f'{type(self).__name__}(x={self.x!r}, y={self.y!r})'

You could compare it:

    >>> from timeit import timeit
    >>> timeit('repr(Coordinates(2,3))', 'from __main__ import Coordinates')
    1.3057148279999993
    >>> timeit('repr(Point(2,3))', 'from __main__ import Point')
    1.3024310119999996
    >>> 

That's more-or-less it.  At least for now.


        
