from babyfood.io.DrillWriter import DrillWriter
from babyfood.layers import TransformationLayer
from babyfood.pcb.PCBUnits import toMM, toInch


class DrillLayer(DrillWriter, TransformationLayer):
    def __init__(self, *args, **kwargs):
        DrillWriter.__init__(self, *args, **kwargs)
        self._uc = {"METRIC": toMM, "INCH": toInch}[self._units]

    def addHole(self, x, y, d):
        # Unit convert it all
        x = self._uc(x)
        y = self._uc(y)
        d = self._uc(d)

        # Scale/move
        x, y = self._ht.project(((x, y)))
        d = self._ht.scale(d)

        # Write it to the file
        self._addHole(x, y, d)

    def addHoles(self, xs, ys, ds):
        """
        Add holes based on three (x, y, d) interators.
        """
        self._fCheck()
        for x, y, d in zip(xs, ys, ds):
            self.addHole(x, y, d)
