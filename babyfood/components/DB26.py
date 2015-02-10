from babyfood.pcb.PCBUnits import toMM
from babyfood.features.basic import CircularVia, CenteredRectangle


# http://portal.fciconnect.com/Comergent//fci/drawing/c-cd-0021.pdf
class DB26:
    def __init__(self):
        self._a = toMM(39.14)
        self._b = toMM(33.32)
        self._c = toMM(25.18)
        self._d = toMM(24.54)
        self._e = toMM(7.02)
        self._f = toMM(8.01)
        self._g = toMM(2.285)

    def _computePinCoords(self):
        # Top row
        y = 2.54 / 2
        for n in range(9):
            x = ((self._b / 2) - self._f) - (self._g * n)
            yield x, y

        # Middle row
        y = 0
        for n in range(9):
            x = ((self._b / 2) - self._f) - (self._g * (n - 0.5))
            yield x, y

        y = -2.54 / 2
        for n in range(8):
            x = ((self._b / 2) - self._f) - (self._g * n)
            yield x, y

    def draw(self, ctx):
        # Mounting holes
        mHole = CircularVia(toMM(3.7 / 2), toMM(3.2 / 2))

        for spacing in (-self._b / 2, +self._b / 2):
            with ctx.transform.translation(spacing, 0):
                mHole.draw(ctx)

        pinPrint = CircularVia(toMM(1.2 / 2), toMM(0.90 / 2))
        for xS, yS in self._computePinCoords():
            with ctx.transform.translation(xS, yS):
                pinPrint.draw(ctx)

        # Connector foot-print
        yBack = -2.54
        yFront = 11.43

        yMiddle = (yBack + yFront) / 2
        yLength = yFront - yBack

        ctx.setActiveLayer("overlay")
        outline = CenteredRectangle(self._a, yLength)
        with ctx.transform.translation(0, yMiddle):
            outline.draw(ctx)

        yConFront = yFront + 6.17
        connLength = yConFront - yBack
        connCP = (yConFront + yBack) / 2
        connOutline = CenteredRectangle(self._d, connLength)
        with ctx.transform.translation(0, connCP):
            connOutline.draw(ctx)
