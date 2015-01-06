from warnings import warn

import numpy as np


class HomogenousTransform:
    def __init__(self, m=None):
        if m is None:
            m = np.eye(3)
        assert m.shape == (3, 3)
        self.m = np.matrix(m)
        self._checkDeterminant()

    def _checkDeterminant(self):
        determinant = np.linalg.det(self.m)
        assert not np.allclose(determinant, 0)

    def scale(self, value):
        if self.m[0, 0] != self.m[1, 1]:
            warn("scale called with non-uniform expansion!")
        return value * self.m[0, 0]

    def project(self, xys):
        assert xys.shape[0] == 2
        length = xys.shape[1]
        paddin = np.ones((1, length))
        xyw = np.concatenate((xys, paddin), axis=0)
        prod = self.m * xyw
        prod /= prod[2, :]
        return prod[0:2, :]

    def __mul__(self, other):
        return HomogenousTransform(self.m * other.m)

    @staticmethod
    def rotation(phi):
        # MRG TODO: Unit convert here.
        s = np.sin
        c = np.cos
        m = np.matrix([[c(phi), -s(phi), 0],
                       [s(phi),  c(phi), 0],
                       [0,       0,      1]])
        return HomogenousTransform(m)

    @staticmethod
    def translation(dx, dy):
        m = np.matrix([[1, 0, dx],
                       [0, 1, dy],
                       [0, 0,  1]])
        return HomogenousTransform(m)

    @staticmethod
    def scaling(s):
        m = np.matrix([[s, 0, 0],
                       [0, s, 0],
                       [0, 0, 1]])
        return HomogenousTransform(m)


class TransformationContext:
    def __init__(self, m=None):
        self.xformStack = [HomogenousTransform(m)]
        self._updateXform()

        tMethods = {"__init__": self._transform_init,
                    "__enter__": self._translation_entr,
                    "__exit__": self._popXform}
        self.translation = type("", (), tMethods)

        rMethods = {"__init__": self._transform_init,
                    "__enter__": self._rotation_entr,
                    "__exit__": self._popXform}
        self.rotation = type("", (), rMethods)

    def _transform_init(self, *args):
        self._t = args

    def _translation_entr(self):
        self.addTranslation(*self._t)
        del self._t

    def _rotation_entr(self):
        self.addRotation(*self._t)
        del self._t

    def _updateXform(self):
        self._m = HomogenousTransform()
        for xform in self.xformStack:
            self._m = self._m * xform

    def _pushXform(self, ht):
        self.xformStack.append(ht)
        self._updateXform()

    def _popXform(self, *args):
        self.xformStack.pop()
        self._updateXform()

    def addTranslation(self, x, y):
        ht = HomogenousTransform.translation(x, y)
        self._pushXform(ht)

    def addRotation(self, phi):
        ht = HomogenousTransform.rotation(phi)
        self._pushXform(ht)

    def project(self, xys):
        return self._m.project(xys)
