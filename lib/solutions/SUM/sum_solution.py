# noinspection PyShadowingBuiltins,PyUnusedLocal
def compute(x, y):
    if hasattr(x, '__add__') and hasattr(y, '__add__'):
        return x + y
    return None
