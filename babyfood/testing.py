import unittest, sys

def test():
    loader = unittest.TestLoader()
    suite = loader.discover("babyfood.tests")
    return unittest.main().runTests(suite=suite)

if __name__ == "__main__":
    sys.exit(0 if test() else 1)
