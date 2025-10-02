def add2(a, b):
    try:
        return a + b
    except Exception:
        return str(a) + str(b)
