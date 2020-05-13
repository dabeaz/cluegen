# cluegen - Data Classes From Type Clues

Cluegen is a library that allows you to define data classes using
Python type clues. Here's an example of how you use it:

```python
from cluegen import Datum

class Coordinates(Datum):
    x: int
    y: int
```

The resulting class works in a well civilised way, providing the
usual `__init__()` and `__repr__()` methods that you'd normally have
to type out by hand:

```python
>>> a = Coordinates(2, 3)
>>> a
Coordinates(x=2, y=3)
>>> a.x
2
>>> a.y
3
>>> 
```

Inheritance works as well--if you add new attributes in a subclass they 
get added to the already existing attributes.  For example:

```python
class Coordinates3(Coordinates):
    z : int

>>> c = Coordinates3(1,2,3)
>>> c
Coordinates3(x=1, y=2, z=3)
>>> 
```

It's easy!

## Wait, hasn't this already been invented?

At this point, naysayers will be quick to point out that "well,
actually you could just use `@dataclass` from the standard library." 
Othe.rs migh.t help.fully sugg.est usag.e of the attr.s libr.ary.
And they might have a point.  I mean, sure, you could write your class
like this:

```python
from dataclasses import dataclass

@dataclass
class Coordinates:
    x: int
    y: int
```

Yes. Yes, you could do that if you wanted your class to be slow to
import, wrapped up by more than 1000 lines of tangled decorator magic,
and inflexible. Or you could use cluegen! Cluegen is tiny, extensible,
provides the same notational convenience, and results in classes that
import about 20x faster (see the file `perf.py` for a benchmark).

Under the hood, `cluegen` works by dynamically creating code for
methods such as `__init__()` and `__repr__()`.  This code looks
exactly the same as code you would normally write by hand.  It's the
same kind of code that the `@dataclass` decorator creates. A notable
feature of `cluegen` however, is that all of its code generation is
"lazy."  That is, no methods are generated until they're actually
needed during the execution of your program.  This substantially
reduces import and startup time for situations where a program might
only be using a subset of the defined data classes. You also don't pay
a penalty for features you aren't using.  And even if do use all the
features, it's still faster than dataclasses. Phfft!

## Extending Cluegen

`cluegen` is customizable in interesting ways.  For example, suppose
you wanted to add your own custom code generation method to the
`Datum` class.  Here's an example of how you could do that:

```python
from cluegen import Datum, cluegen, all_clues

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
```

Now, a test:

```python
>>> p = Point(2,3)
>>> p.as_dict()
{ 'x': 2, 'y': 3 }
>>>
```

In the above example, the decorated `as_dict()` method is presented
the class.  In this case, `cls` would be `Point`. The `all_clues()`
function is a utility function that collects all type-clues from a
class including those from base classes.  For this example, it returns
a dictionary `{'x': int, 'y': int}`.  The value returned by
`as_dict()` is a text-string containing the implementation of the
actual `as_dict()` method as it would be if you had written it by
hand.  This text string is executed once to create a method that
replaces the decorated version.  From that point forward, the class
uses the generated code instead.

`cluegen` doesn't have too many other bells and whistles--the entire
implementation is about 100 lines of code.  It's something that you
can understand, modify, and play around with.  

## A True Story

Once, there was this developer. For the sake of this story, let's call
him "Dave."  As Dave was want to do, he liked to write compilers.  A
compiler is a natural place to use something fancy like a
dataclass--especially for all of the tree structures.  So, Dave did just that:

```python
from dataclasses import dataclass

@dataclass
class Node:
    pass

@dataclass
class Expression(Node):
    pass

@dataclass
class Statement(Node):
    pass

@dataclass
class Integer(Expression):
    value: int

@dataclass
class BinOp(Expression):
    op: str
    left: Expression
    right: Expression

@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression

@dataclass
class PrintStatement(Statement):
    value: Expression

# Example
node = PrintStatement(BinOp('+', Integer(3), BinOp('*', Integer(4), Integer(5))))
```

This all worked great--better than expected in fact.  However, one day, Dave thought it would
be useful to add an optional line number attribute to all of the nodes.  Naturally, this
seemed like something that could be easily done on the base class:

```python
@dataclass
class Node:
    lineno:int = None
```

Dave thought wrong! Dataclasses explode in a fireball if you do this.
No, not optional attributes.  Not, base classes. Alas, the only
solution seemed to involve copying a `lineno` attribute to end of
every class.  If Dave had had a clue about cluegen, he could have easily
solved this problem by just adding a minor tweak to the code generation for `__init__()`:

```python
from cluegen import Datum, all_clues, cluegen

class Nodum(Datum):
    lineno = None
    @cluegen
    def __init__(cls):
        clues = all_clues(cls)
        args = ', '.join(f'{name}={getattr(cls,name)!r}'
                         if hasattr(cls, name) and not isinstance(getattr(cls, name), types.MemberDescriptorType) else name
                         for name in clues)
        body = '\n'.join(f'    self.{name} = {name}' for name in clues)
        body += '\n    self.lineno = lineno'   
        return f'def __init__(self, {args}, *, lineno=None):\n{body}\n'

class Expression(Nodum):
    pass

class Statement(Nodum):
    pass

class Integer(Expression):
    value: int

class BinOp(Expression):
    op: str
    left: Expression
    right: Expression

class UnaryOp(Expression):
    op: str
    operand: Expression

class PrintStatement(Statement):
    value: Expression
```

Now, it works exactly as desired:

```python
>>> a = Integer(23)
>>> b = Integer(23, lineno=123)
>>> b.value
23
>>> b.lineno
123
>>>
```

The moral of this story is that cluegen represents a different kind a
power--the power to do what YOU want as opposed what THEY allow. It's
all about YOU!

## Making Your Own Datum Class

The provided `Datum` class generates code for a common set of default
methods.  You really don't need to use this if you want to go in a
completely different direction.   For example, suppose that you 
wanted to abandon type hints and generate code based on `__slots__`
instead.  Here's an example of how you could do it:

```python
from cluegen import DatumBase, cluegen

def all_slots(cls):
    slots = []
    for cls in cls.__mro__:
        slots[0:0] = getattr(cls, '__slots__', [])
    return slots

class Slotum(DatumBase):
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
```

Some of the string formatting might take a bit of pondering.  However, here is an
example of how you'd use `Slotum`:

```python
>>> class Point(Slotum):
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
```

## Theory of Operation

Cluegen is based on Python's descriptor protocol.  In a nutshell, whenever
you access an attribute of a class, Python looks for an object that 
implements a magic `__get__()` method.  If found, it invokes `__get__()`
with the associated instance and class.  Cluegen uses this to generate
code on first-access to special methods such as `__init__()`.  Here 
is an example of the machinery at work.

First, define a class:

```python
>>> class Point(Datum):
...     x: int
...     y: int
... 
>>>
```

Now, look at the `__init__()` method in the class dictionary.  You'll
see that's some kind of strange "ClueGen" instance:

```python
>>> Point.__dict__['__init__']
<__main__.ClueGen___init__ object at 0x102ec1240>
>>> 
```

This object represents the "ungenerated" method.  If you touch the
`__init__` attribute on the class in any way, you'll see the Cluegen
object disappear and be replaced by a proper function:

```python
>>> Point.__init__
<function __init__ at 0x102e208c8>
>>> Point.__dict__['__init__']
<function __init__ at 0x102e208c8>
>>> 
```

This is the basic idea--code generation on first access to an
attribute. Inheritance adds an extra wrinkle into the equation.
Suppose you define a subclass:

```python
>>> class Point3(Point):
...     z: int
... 
>>> Point3.__dict__['__init__']
<__main__.ClueGen___init__ object at 0x102ec1240>
>>> 
```

Here, you'll see the "ClueGen" object make a return to the class dictionary.
Again, it gets replaced when it's first accessed.  Here's what happens
at a low level when you make an instance:

```python
>>> i = Point3.__dict__['__init__']
>>> i.__get__(None, Point3)
<function __init__ at 0x102e20950>
>>> Point3.__init__
<function __init__ at 0x102e20950>
>>> p = Point3(1,2,3)
>>> p
Point3(x=1, y=2, z=3)
>>> 
```

For more reading, look for information on Python's "Descriptor Protocol."
This is the same machinery that makes properties, classmethods, and other
features of the object system work.

## Questions and Answers

**Q: What methods does `cluegen` generate?**

A: By default it generates `__init__()`, `__repr__()`, `__iter__()`,
and `__eq__()` methods.

**Q: Does `cluegen` enforce the specified types?**

A: No. The types are merely clues about what the value might be and
the Python language does not provide any enforcement on its own.  The
types might be useful in an IDE or third-party tools that perform
type-checking or linting.  You could probably extend `cluegen` to
enforce types if you wanted though.

**Q: Does `cluegen` use any advanced magic such as metaclasses?**

A: No. The `Datum` base class is a plain Python class.  It defines an
`__init_subclass__()` method to assist with the management of
subclasses, but nothing other than the standard special methods
such as `__init__()`, `__repr__()`, `__iter__()`, and `__eq__()` are
defined.  Python's descriptor protocol is used to drive code generation.

**Q: How do I install `cluegen`?**

A: There is no `setup.py` file, installer, or an official release. You
install it by copying the code into your own project. `cluegen.py` is
small. You are encouraged to copy and modify it to your own purposes.

**Q: But what if new features get added?**

A: What new features?  The best new features are no new features. 

**Q: How do you pronounce and use `cluegen` in a sentence?**

A: You should pronounce it as "kludg-in" as in "runnin" or "trippin".
So, if someone asks "what are you doing?", you don't say "I'm using
cluegen."  No, you'd say "I'm kludgin up some classes."  The latter is
more accurate as it describes both the tool and the thing that you're
actually doing.  Accuracy matters.

**Q: How do you pronounce and use `cluegen` while live-streaming?**

A: "Oh. Oh. I'm totally kludgin it! Yes! YES! YES!!! OH! MY! GOD!!!!!"

**Q: Who maintains cluegen?**

A: If you're using it, you do. You maintain cluegen.

**Q: Who wrote this?**

A: `cluegen` is the work of David Beazley. http://www.dabeaz.com.

        
