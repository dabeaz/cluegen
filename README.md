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

    from cluegen import Datum, cluegen, all_clues

    class MyDatum(Datum):
        @cluegen
        def as_dict(cls):
            clues = all_clues(cls)
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
the class.  In this case, `cls`
would be `Point`. The `all_clues()` function is a utility function that
collects all type-clues from a class including those from base classes.
For this example, it returns a dictionary `{'x': int, 'y':
int}`.  The value returned by `as_dict()` is a text-string containing
the implementation of the actual `as_dict()` method as it would be if
you had written it by hand.  This text string is executed once to
create a method that replaces the decorated version.  From that point
forward, the class uses the generated code instead.

`cluegen` doesn't have too many other bells and whistles--the entire
implementation is about 100 lines of code.  It's something that you
can understand, modify, and play around with.  

## Making Your Own Datum Class

The provided `Datum` class generates code for a common set of default
methods.  You really don't need to use this if you want to go in a
completely different direction.   For example, suppose that you 
wanted to abandon type hints and generate code based on `__slots__`
instead.  Here's an example of how you could do it:

    from cluegen import DatumBase, cluegen

    def all_slots(cls):
        slots = []
        for cls in cls.__mro__:
            slots[0:0] = getattr(cls, '__slots__', [])
        return slots

    class SlotDatum(DatumBase):
        __slots__ = ()
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

Some of the string formatting might take a bit of pondering.  However, here is an
example of how you'd use `SlotDatum`:

    >>> class Point(SlotDatum):
    ...     __slots__ = ('x', 'y')
    ... 
    >>> p = Point(2,3)
    >>> p
    Point(x=2,y=3)
    >>> class Point3(Point):
    ...     __slots__ = ('z',)
    ... 
    >>> p3 = Point3(2,3,4)
    >>> p3
    Point3(x=2,y=3,z=4)
    >>> 


## Theory of Operation

Cluegen is based on Python's descriptor protocol.  In a nutshell, whenever
you access an attribute of a class, Python looks for an object that 
implements a magic `__get__()` method.  If found, it invokes `__get__()`
with the associated instance and class.  Cluegen uses this to generate
code on first-access to special methods such as `__init__()`.  Here 
is an example of the machinery at work.

First, define a class:

    >>> class Point(Datum):
    ...     x: int
    ...     y: int
    ... 
    >>>

Now, look at the `__init__()` method in the class dictionary.  You'll
see that's some kind of strange "ClueGen" instance:

    >>> Point.__dict__['__init__']
    <__main__.ClueGen___init__ object at 0x102ec1240>
    >>> 

This object represents the "unevaluated" method.  If you touch the
`__init__` attribute on the class in any way, you'll see the Cluegen
object disappear and be replaced by a proper function:

    >>> Point.__init__
    <function __init__ at 0x102e208c8>
    >>> Point.__dict__['__init__']
    <function __init__ at 0x102e208c8>
    >>> 

This is the basic idea--code generation on first access to an
attribute. Inheritance adds an extra wrinkle into the equation.
Suppose you define a subclass:

    >>> class Point3(Point):
    ...     z: int
    ... 
    >>> Point3.__dict__['__init__']
    <__main__.ClueGen___init__ object at 0x102ec1240>
    >>> 

Here, you'll see the "ClueGen" object make a return to the class dictionary.
Again, it gets replaced when it's first accessed.  Here's what happens
at a low level when you make an instance:

    >>> i = Point3.__dict__['__init__']
    >>> i.__get__(None, Point3)
    <function __init__ at 0x102e20950>
    >>> Point3.__init__
    <function __init__ at 0x102e20950>
    >>> p = Point3(1,2,3)
    >>> p
    Point3(x=1, y=2, z=3)
    >>> 

For more reading, look for information on Python's "Descriptor Protocol."
This is the same machinery that makes properties, classmethods, and other
features of the object system work.

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
defined.  Python's descriptor protocol is used to drive code generation.

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

**Q: Who maintains cluegen?**

A: `cluegen` is the work of David Beazley. http://www.dabeaz.com.

        
