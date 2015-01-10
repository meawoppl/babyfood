from babyfood.io.DrillWriter import DrillWriter
from babyfood.layers import TransformationLayer
from babyfood.PCBUnits import mm, inch


class DrillLayer(DrillWriter, TransformationLayer):
    def __init__(self, *args, **kwargs):
        self._uc = {"MM": mm, "IN": inch}[self._units]

    def addHoles(self, xs, ys, ds):
        """
        Add holes based on three (x,y,d) interators.
        """
        self._fCheck()
        for x, y, d in zip(xs, ys, ds):
            self.addHole(x, y, d)
