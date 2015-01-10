from babyfood.homogenous import HomogenousTransform


class TransformationLayer:
    _ht = HomogenousTransform()

    def setTransformMatrix(self, xform):
        self._ht = xform

    def getTransformMatrix(self):
        return self._ht
