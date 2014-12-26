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
    def scale(sx, sy):
        m = np.matrix([[sx, 0, 0],
                       [0, sy, 0],
                       [0,  0, 1]])
        return HomogenousTransform(m)


class TransformationContext:
    def save(self):
        pass
    def load(self):
        pass


if __name__ == "__main__":
    ht = HomogenousTransform.translation(5, 5)

    ht2 = ht * ht
    
    xy = np.ones((2, 10))
    r = ht2.project(xy)
    print(r)
