import sys
from src.calc import add2

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: add2vals x y")
        sys.exit(1)
    a, b = sys.argv[1], sys.argv[2]
    print(add2(a, b))
