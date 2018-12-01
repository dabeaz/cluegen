# cluegen - Classes from type clues

Cluegen is a library that allows classes to be easily created by
Python type clues. Here how it works. First, you create a base class
where you pick the features that you want:

    from cluegen import Init, Repr

    class Base(Init, Repr):
        pass

In this example, the `Base` class creates an `__init__()` and an
`__repr__()` method for you. Next, you start defining your classes:

    class Coordinates(Base):
        x: int
        y: int

    class Holding(Base):
        name: str
        shares: int
        price: float

Here's how the resulting classes work:

   >>> a = Coordinates(2, 3)
   >>> a
   Coordinates(x=2, y=3)
   >>> a.x
   2
   >>> a.y
   3
   >>> 
   >>> b = Holding(name='ACME', shares=50, price=123.45)
   >>> b
   Holding(name='ACME', shares=50, price=123.45)
   >>>

That's more-or-less it.  At least for now.


        
