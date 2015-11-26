from warnings import warn

import numpy as np

from babyfood.io.GerberWriter import GerberWriter
from babyfood.layers import TransformationLayer
from babyfood.pcb.PCBUnits import toMM, toInch


def pointsClose(pt1, pt2, eps=1e-8):
    x1, y1 = pt1
    x2, y2 = pt2

    dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist < eps


class GerberLayer(GerberWriter, TransformationLayer):
    def __init__(self, *args, **kwargs):
        '''
        GerberLayer is a class for producing gerber vector graphics
        It uses the GerberWriter base class to do the file-io and
        sanity checks, and provides a slightly higher level interface
        to make graphics easier.  This includes:
          1. Transforms
          2. Mandatory unit checks
          3. Simplified aperature definitions
          4. Lots of Semantic-Sugar
        '''
        GerberWriter.__init__(self, *args, **kwargs)
        pmMethods = {"__enter__": self._startPolygonMode,
                     "__exit__": self._stopPolygonMode}
        self.polygonMode = type("PolygonMode", (), pmMethods)

        self._uc = {"MM": toMM, "IN": toInch}[self._units]

        # Predefine a circular aperature with 0 size.
        self.defineCircularAperature(0)

    def _holeHelper(self, hole):
        assert len(hole) <= 2

        # Get the unit conversions out of the way
        hole = [self._uc(h) for h in hole]

        # Nota hole
        if len(hole) == 0:
            return ""

        # Circular hole
        if len(hole) == 1:
            # unit-convert and scale it
            ucs = self._ht.scale(hole[0])
            fStr = self._trimFloatToPrecision(ucs, radix=".")
            return "X" + fStr

        if len(hole) == 2:
            length, width = self._ht.project(((hole[0] / 2, hole[1] / 2)))
            lStr = self._trimFloatToPrecision(length, radix=".")
            wStr = self._trimFloatToPrecision(width, radix=".")
            return "X" + lStr + "X" + wStr

    def defineCircularAperature(self, diameter, hole=tuple(), setAsCurrent=True):
        assert diameter >= 0, "Circular aperature must be >= 0"
        # Scale and convert the circle
        d = self._ht.scale(self._uc(diameter))

        # Format
        rStr = self._trimFloatToPrecision(d, radix=".")

        # Register/return
        aprDescriptor = "C," + rStr + self._holeHelper(hole)
        return self._defineAperature(aprDescriptor, setAsCurrent)

    def _rectObAperature(self, ro, xSize, ySize, hole=tuple(), setAsCurrent=True):
        assert ro in ["R", "O"]
        assert xSize > 0
        assert ySize > 0

        # Unit convert
        x = self._uc(xSize)
        y = self._uc(ySize)

        # Project
        x, y = self._ht.project(((x, y)))

        # Format
        xStr = self._trimFloatToPrecision(x, radix=".")
        yStr = self._trimFloatToPrecision(y, radix=".")

        # Register/return
        aprDescriptor = ro + "," + xStr + "X" + yStr + self._holeHelper(hole)
        return self._defineAperature(aprDescriptor, setAsCurrent)

    def defineRectangularAperature(self, xSize, ySize, hole=tuple(), setAsCurrent=True):
        self._rectObAperature("R", xSize, ySize, hole=hole, setAsCurrent=setAsCurrent)

    def defineObroundAperature(self, xSize, ySize, hole=tuple(), setAsCurrent=True):
        self._rectObAperature("O", xSize, ySize, hole=hole, setAsCurrent=setAsCurrent)

    def definePolygonAperature(self):
        raise NotImplemented()

    def moveTo(self, newX, newY):
        newX = self._uc(newX)
        newY = self._uc(newY)
        px, py = self._ht.project(((newX, newY)))
        self._linearMove(px, py, 2)

    def lineTo(self, newX, newY):
        newX = self._uc(newX)
        newY = self._uc(newY)
        px, py = self._ht.project(((newX, newY)))
        self._linearMove(px, py, 1)

    def flashAt(self, newX, newY):
        newX = self._uc(newX)
        newY = self._uc(newY)
        px, py = self._ht.project(((newX, newY)))
        self._linearMove(px, py, 3)

    def arcLineTo(self, endX, endY, cX, cY, direction):
        endX = self._uc(endX)
        endY = self._uc(endY)

        cX = self._uc(cX)
        cY = self._uc(cX)

        pex, pey = self._ht.project(((endX, endY)))
        pcx, pcy = self._ht.project(((cX, cY)))
        self._arcMove(pex, pey, pcx, pcy, direction)

    def circle(self, cx, cy, cr):
        assert cr > 0
        self.moveTo(cx - cr, cy)
        self.arcLineTo(cx - cr, cy, cx, cy, "CW")

    def polygon(self, xs, ys):
        """
        This subroutine writes a polygon to the gerbv file.
        Note that this polygon can be fairly complex, including
        null-contours and nested shapes.  Refer to the gerber
        spec to see what sorts of things are allowed in here.
        """
        with self.polygonMode():
            for n, (xC, yC) in enumerate(zip(xs, ys)):
                if n == 0:
                    # Move to the start point
                    self.moveTo(xC, yC)
                else:
                    # Trace the next segment
                    self.lineTo(xC, yC)
            # If the start and end points are not equal, close the loop
            if not pointsClose((xs[0], ys[0]), (xs[-1], ys[-1])):
                self.lineTo(xs[0], ys[0])
                warn("WARNING: Call to polygon() is getting automatically closed!")

    def filledCircle(self, x, y, r):
        with self.polygonMode():
            self.circle(x, y, r)
