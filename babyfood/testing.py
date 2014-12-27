import os, unittest, sys

import babyfood.tests


def test():
    return unittest.main(babyfood.tests)

if __name__ == "__main__":
    sys.exit(0 if test() else 1)
