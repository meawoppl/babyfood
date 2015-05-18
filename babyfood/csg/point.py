import numpy as np


class Point:
    def __init__(self, x, y):
        self.xy = np.array((x, y), dtype=np.float64)

    def __eq__(self, other):
        return np.allclose(self.xy, other.xy)
