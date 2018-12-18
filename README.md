# cluegen - Data Classes From Type Clues

Cluegen is a library that allows you to define data classes using
Python type clues. Here's an example of how you use it:

    from cluegen import Datum

    class Coordinates(Datum):
        x: int
        y: int

The resulting class works in a friendly way, providing the usual
`__init__()` and `__repr__()` methods that you'd normally have to
write by hand:

    >>> a = Coordinates(2, 3)
    >>> a
    Coordinates(x=2, y=3)
    >>> a.x
    2
    >>> a.y
    3
    >>> 

And the runtime performance is the same as defining a similar class by
hand.  For example, suppose you wrote this class instead:

    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __repr__(self):
            return f'{type(self).__name__}(x={self.x!r}, y={self.y!r})'

You could compare its performance:

    >>> from timeit import timeit
    >>> timeit('repr(Coordinates(2,3))', 'from __main__ import Coordinates')
    1.3057148279999993
    >>> timeit('repr(Point(2,3))', 'from __main__ import Point')
    1.3024310119999996
    >>> 

Inheritance works as well--if you add new attributes they will be added to the
already existing attributes.  For example:

    class Coordinates3(Coordinates):
        z : int

In this case, various methods will be extended to include the extra value:

    >>> c = Coordinates3(1,2,3)
    >>> c
    Coordinates3(x=1, y=2, z=3)
    >>> 

Under the hood, `cluegen` works by dynamically creating code for 
methods such as `__init__()` and `__repr__()`.  This code looks
exactly the same as code you would normally write by hand.  A
notable feature of `cluegen` however, is that all of its code
generation is "lazy."  That is, no methods are generated until they're
actually needed during the execution of your program.  This substantially reduces import
and startup time for situations where a program might only be using a
subset of the defined data classes. You also don't pay a penalty for
features you aren't using. Take a look at the `perf.py` file to see a
performance test. 

## Extending Cluegen

`cluegen` is customizable in interesting ways.  For example, suppose you
wanted to add your own custom code generation method to the `Datum` 
class.  Here's an example of how you could do that:

    from cluegen import Datum, cluegen

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

Now, a test:

    >>> p = Point(2,3)
    >>> p.as_dict()
    { 'x': 2, 'y': 3 }
    >>>

In the above example, the decorated `as_dict()` method is presented
with information about the class and a dictionary of all collected
type clues (including those from base classes).  In this case, `cls`
would be `Point` and `clues` would be a dictionary `{'x': int, 'y':
int}`.  The value returned by `as_dict()` is a text-string containing
the implementation of the actual `as_dict()` method as it would be if
you had written it by hand.  This text string is executed once to
create a method that replaces the decorated version.  From that point
forward, the class uses the generated code instead.

`cluegen` doesn't have too many other bells and whistles--the entire
implementation is about 100 lines of code.  It's something that you
can understand, modify, and play around with.  

## Questions and Answers

**Q: What methods does `cluegen` generate?**

A: By default it generates `__init__()`, `__repr__()`, `__iter__()`,
and `__eq__()` methods.

**Q: Does `cluegen` enforce the specified types?**

A: No. The types are merely clues about what the value might be
and the Python language does not provide any enforcement on its own.
The types might be useful in an IDE or third-party tools that
perform type-checking or linting.  You could probably extend `cluegen`
to enforce types if you wanted though.

**Q: Does `cluegen` use any advanced magic such as metaclasses?**

A: No. The `Datum` base class is plain Python class.  It defines an
`__init_subclass__()` method to assist with the management of
subclasses, but nothing other than the standard special methods
such as `__init__()`, `__repr__()`, `__iter__()`, and `__eq__()` are
defined.

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

A: No. `cluegen` generates useful data classes in a way that is fast,
simple, and small.
        
