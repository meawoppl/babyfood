from warnings import warn

import numpy as np

from babyfood.io.GerberWriter import GerberWriter
from babyfood.homogenous import HomogenousTransform
from babyfood.PCBUnits import mm, inch


def pointsClose(pt1, pt2, eps=1e-8):
    x1, y1 = pt1
    x2, y2 = pt2

    dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist < eps


class GerberLayer(GerberWriter):
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
        self.polygonMode = type("PolygonMode", (), {"__enter__": self._startPolygonMode,
                                                    "__exit__": self._stopPolygonMode})

        self._m = HomogenousTransform()

        self._uc = {"MM": mm, "IN": inch}[self._units]

    def setTransformMatrix(self, xform):
        self._m = xform

    def defineCircularAperature(self, diameter, setAsCurrent=True):
        aprDescriptor = "C,%0.03f" % diameter
        aprCode = self._defineAperature(aprDescriptor, setAsCurrent)
        return aprCode

    def moveTo(self, newX, newY):
        self._linearMove(newX, newY, 2)

    def lineTo(self, newX, newY):
        self._linearMove(newX, newY, 1)

    def flashAt(self, newX, newY):
        self._linearMove(newX, newY, 3)

    def circle(self, cx, cy, cr):
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
                    self._linearMove(xC, yC, 2)
                else:
                    # Trace the next segment
                    self._linearMove(xC, yC, 1)
            # If the start and end points are not equal, close the loop
            if not pointsClose((xs[0], ys[0]), (xs[-1], ys[-1])):
                self._linearMove(xs[0], ys[0], 1)
                warn("WARNING: Call to polygon() is getting automatically closed!")

    def filledCircle(self, x, y, r):
        with self.polygonMode():
            self.circle(x, y, r)
