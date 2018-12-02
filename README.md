# cluegen - Data Classes From Type Clues

Cluegen is a library that allows you to define data classes using
Python type clues. Here how it works. First, you pick the features
that you want and you put them in a base class:

    import cluegen

    class Base(cluegen.Init, cluegen.Repr):
        pass

In this example, `Base` provides an `__init__()` and a `__repr__()`
method for you (naturally, you could also put other methods in
`Base` if you wanted). Next, you start defining your classes via
inheritance:

    class Coordinates(Base):
        x: int
        y: int

The resulting class works exactly as you want it to:

    >>> a = Coordinates(2, 3)
    >>> a
    Coordinates(x=2, y=3)
    >>> a.x
    2
    >>> a.y
    3
    >>> 

And the performance is the same as defining a similar class by hand.
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

Inheritance should work fine too:

    class Coordinates3(Coordinates):
        z : int

In this case, the `__init__()` and `__repr__()` methods will be extended
to include the extra value:

    >>> c = Coordinates3(1,2,3)
    >>> c
    Coordinates3(x=1, y=2, z=3)
    >>> 

On the surface, `cluegen` might look similar to popular libraries such
as `dataclasses` or `attrs`.  Under the hood, all of these libraries work by
dynamically creating code at class definition time.  That is, they
generate methods for you by creating source code fragments, executing
them using the `exec()` function, and attaching the resulting methods
to your class.

`cluegen` works in a similar way except that all code generation is
"lazy."  That is, no methods are generated until they're actually
needed during execution.  This substantially reduces import and startup
time for situations where a program might only be using a subset of the
defined data classes.

`cluegen` doesn't have many other bells and whistles--the entire
implementation is under 100 lines of code.  It's something that you
can easily understand, modify, and play around with.






        
