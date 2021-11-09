# Example of using the Python 3.10 match statement

from cluegen import Datum

class Expression(Datum):
    pass

class Integer(Expression):
    value: int

class BinOp(Expression):
    op: str
    left: Expression
    right: Expression

expr = BinOp('+', BinOp('*', Integer(3), Integer(4)),
                  BinOp('*', Integer(5), Integer(6)))

def evaluate(expr:Expression):
    match expr:
        case Integer(value):
             return value
        case BinOp('+', left, right):
             return evaluate(left) + evaluate(right)
        case BinOp('*', left, right):
             return evaluate(left) * evaluate(right)
        case _:
             raise RuntimeError()

print(evaluate(expr))

