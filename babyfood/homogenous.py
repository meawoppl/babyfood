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

    def isIsotropicScale(self):
        return np.abs(self.m[0, 0]) == np.abs(self.m[1, 1])

    def scale(self, value):
        if not self.isIsotropicScale():
            warn("scale() called with non-uniform expansion!")

        projected0 = self.project([[0, 0]])
        projected1 = self.project([[1, 0]])

        pDelta = projected1 - projected0
        scale = np.sqrt(np.sum(pDelta * pDelta))

        return value * scale

    def project(self, xys):
        xys = np.array(xys).reshape((2, -1))
        assert xys.shape[0] == 2
        length = xys.shape[1]
        paddin = np.ones((1, length))
        xyw = np.concatenate((xys, paddin), axis=0)
        prod = self.m * xyw
        prod /= prod[2, :]
        return np.array(prod[0:2, :])

    def __mul__(self, other):
        return HomogenousTransform(self.m * other.m)

    @staticmethod
    def rotation(phi):
        # MRG TODO: Unit convert here.
        s = np.sin
        c = np.cos
        m = np.matrix([[c(phi), -s(phi), 0],
                       [s(phi), +c(phi), 0],
                       [000000, 0000000, 1]])
        return HomogenousTransform(m)

    @staticmethod
    def translation(dx, dy):
        m = np.matrix([[1, 0, dx],
                       [0, 1, dy],
                       [0, 0, 1]])
        return HomogenousTransform(m)

    @staticmethod
    def scaling(s):
        m = np.matrix([[s, 0, 0],
                       [0, s, 0],
                       [0, 0, 1]])
        return HomogenousTransform(m)


class TransformationContext(HomogenousTransform):
    def __init__(self, m=None):
        HomogenousTransform.__init__(self)
        self.xformStack = [HomogenousTransform(m)]
        self._updateXform()

        # Make the "with transform" handles
        self.translation = self._mfgTransform(self._tr_entr)
        self.rotation = self._mfgTransform(self._ro_entr)
        self.flipX = self._mfgTransform(self._fx_entr)
        self.flipY = self._mfgTransform(self._fy_entr)

    # Helper for the above with handles
    def _mfgTransform(self, enterFunction):
        tMethods = {"__init__": self._transform_init,
                    "__enter__": enterFunction,
                    "__exit__": self._popXform}
        return type("", (), tMethods)

    def _transform_init(self, *args):
        self._t = args

    def _fx_entr(self):
        m = np.array(((-1, 0, 0),
                      (0, 1, 0),
                      (0, 0, 1)))
        ht = HomogenousTransform(m)
        self._pushXform(ht)
        del self._t

    def _fy_entr(self):
        m = np.array(((1, 0, 0),
                      (0, -1, 0),
                      (0, 0, 1)))
        ht = HomogenousTransform(m)
        self._pushXform(ht)
        del self._t

    def _tr_entr(self):
        self.addTranslation(*self._t)
        del self._t

    def _ro_entr(self):
        self.addRotation(*self._t)
        del self._t

    def _updateXform(self):
        _m = HomogenousTransform()
        for xform in self.xformStack:
            _m = _m * xform

        self.m[:] = _m.m

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

    def getMatrix(self):
        return self.m

    def copyCurrentTransform(self):
        return HomogenousTransform(self.m.copy())
