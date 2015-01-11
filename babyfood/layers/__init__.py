from babyfood.homogenous import HomogenousTransform


class TransformationLayer:
    _ht = HomogenousTransform()

    def setTransformMatrix(self, xform):
        self._ht.m = xform

    def getTransformMatrix(self):
        return self._ht.m
