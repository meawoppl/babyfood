from warnigns import warn
from babyfood.io.GerberWriter import GerberWriter

from babyfoor.homogenous import HomogenousTransform

import numpy as np


def pointsClose(pt1, pt2, eps=1e-8):
    x1, y1 = pt1
    x2, y2 = pt2

    dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist < eps


class GerberLayer(GerberWriter):
    def __init__(self, *args, **kwargs):
        GerberWriter.__init__(self, *args, **kwargs)
        self.polygonMode = type("PolygonMode", (), {"__enter__": self._startPolygonMode,
                                                    "__exit__": self._stopPolygonMode})

        self._m = HomogenousTransform()

    def setTransform(self, xform):
        self._m = xform

    def defineCircularAperature(self, diameter, setAsCurrent=True):
        aprDescriptor = "C,%0.03f" % diameter
        aprCode = self._defineAperature(aprDescriptor, setAsCurrent)
        return aprCode

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
