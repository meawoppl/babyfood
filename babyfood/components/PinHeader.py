import itertools

from math import sqrt

from babyfood.pcb.PCBUnits import toMM
from babyfood.features.basic import CircularVia
from babyfood.components.ABC import AbstractTHComponent

stdSpacing = (toMM(2.54), toMM(2.54))

pinEdgeWidth = 0.64
pinViaDiameter = toMM(sqrt((pinEdgeWidth ** 2) * 2))
stdVia = CircularVia((pinViaDiameter / 2) + 0.4, pinViaDiameter / 2)


# http://portal.fciconnect.com/Comergent//fci/drawing/c-cd-0021.pdf
class PinHeader(AbstractTHComponent):
    def __init__(self, shape=(1, 1), spacing=stdSpacing):
        self.shape = shape
        self.spacing = spacing

    def _computePinCoords(self):
        xC, yC = self.shape
        xS, yS = self.spacing
        xCenter = xS * (xC - 1) / 2
        yCenter = yS * (yC - 1) / 2
        for count, (x, y) in enumerate(itertools.product(range(xC), range(yC))):
            yield count + 1, (x * xS) - xCenter, (y * yS) - yCenter

    def draw(self, ctx):
        for n, x, y in self._computePinCoords():
            with ctx.transform.translation(x, y):
                stdVia.draw(ctx)


# https://www.sparkfun.com/datasheets/Prototyping/Connectors/JST%282%29-01548.pdf
# https://www.sparkfun.com/products/9749
class JSTConnector(AbstractTHComponent):
    def __init__(self, nPins=2, spacing=toMM(2)):
        self._n = nPins
        self._s = spacing

    def _computePinCoords(self):
        xCenter = self._s * (self._n - 1) / 2
        for n in range(self._n):
            xc = (n * self._s) - xCenter
            print(xc)
            yield xc

    def draw(self, ctx):
        # pins + viae
        for x in self._computePinCoords():
            with ctx.transform.translation(x, 0):
                stdVia.draw(ctx)

        # Outline!
        b = toMM((self._n * 2) + 2)
        backEdge = toMM(1.8)
        frontEdge = -toMM(6.25)
        leftEdge = -b / 2
        rightEdge = b / 2

        print(leftEdge, rightEdge)
        ctx.setActiveLayer("overlay")
        ctx.moveTo(leftEdge, backEdge)
        ctx.lineTo(leftEdge, frontEdge)
        ctx.lineTo(rightEdge, frontEdge)
        ctx.lineTo(rightEdge, backEdge)
        ctx.lineTo(leftEdge, backEdge)
