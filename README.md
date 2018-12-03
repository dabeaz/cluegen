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
defined data classes.  Take a look at the `perf.py` file to see a performance
test.  You'll find that importing a large file of classes defined
with `cluegen` is about 15x faster than loading a similar file that
uses dataclasses from the standard library. 

`cluegen` doesn't have many other bells and whistles--the entire
implementation is about 100 lines of code.  It's something that you
can understand, modify, and play around with.

## Questions and Answers

**Q: Does `cluegen` enforce the specified types?**

A: No. The types are merely clues about what the value might be
and the Python language does not provide any enforcement on its own.
The types might be useful in an IDE or third-party tools that
perform type-checking or linting.  You could probably extend `cluegen`
to enforce types if you wanted though.

**Q: How do I install `cluegen`?**

A: There is no `setup.py` file, installer, or an official release. You
install it by copying the code into your own project. `cluegen.py` is
small. You are encouraged to copy and modify it to your own purposes.

**Q: How do you pronounce and use `cluegen` in a sentence?**

A: You should pronounce it as "kludg-in" as in "runnin" or "trippin".
So, if someone asks "what are you doing?", you don't say "I'm using
cluegen."  No, you'd say "I'm cluegin up some classes."  The latter is
more accurate as it describes both the tool and the thing that you're
actually doing.  Accuracy matters.

**Q: Is this some kind of joke?**

A: No. `cluegen` uses a different approach to generating data classes that
is faster, simpler, and smaller than other popular alternatives.  


        
