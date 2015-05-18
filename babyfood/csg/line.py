import numpy as np

from .point import Point


class Line:
    def __init__(self, x1, y1, x2, y2):
        self.xy1 = Point(x1, y1)
        self.xy2 = Point(x2, y2)

        # Store internally in the form of Ax + By + c = 0
        self.a = -1 / (x2 - x1)
        self.b = 1 / (y2 - y1)
        self.c = (-x1 / self.a) + (y1 / self.b)

        self.abc = np.array((self.a, self.b, self.c), dtype=np.float64)
        self.abc /= self.c

        # Compute the unit direction
        dxy = self.xy2.xy - self.xy1.xy
        mag = np.sqrt(np.sum(dxy ** 2))
        self.unit = dxy / mag

    def __eq__(self, otherline):
        return np.allclose(self.abc, otherline.abc)


class LineSegment(Line):
    def __init__(self, x1, y1, x2, y2):
        # Superclass init
        Line.___init__(self, x1, y1, x2, y2)
