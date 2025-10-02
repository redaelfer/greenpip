from src.calc import add2

def test_add_numbers():
    assert add2(1, 2) == 3

def test_add_strings():
    assert add2("a", "b") == "ab"
