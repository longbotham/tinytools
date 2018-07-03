"""This is some info"""

def mytestdivide(x, y):
    """Sample try/except/else/finally for division by zero... Just an
    example to save the appropriate syntax.
    """
    try:
        result = x / y
    except ZeroDivisionError:
        print("division by zero!")
    else:
        print("result is", result)
    finally:
        print("executing finally clause")