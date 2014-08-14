import numpy as np
from PCBBase import PCBFeature, PCBDrawer

import itertools


class AppolonianTest(PCBFeature):
    def __init__(self, scalar):
        PCBFeature.__init__(self)

        self.rs, self.xs, self.ys = np.loadtxt("gasket.csv", skiprows=1, delimiter=",").T / scalar

        # Radaii can be negative (which does make sense really!)
        self.rs = np.abs(self.rs)

        # Find the biggest circle
        maxR = self.rs.max()

        # Rescale everything to mave a max diameter of 3in
        rescalar = (3 * 25.4) / (2 * maxR)
        self.rs *= rescalar
        self.xs *= rescalar
        self.ys *= rescalar

        self.rs -= 0.05 * 2.54

        maxRIndex = self.rs.argmax()
        self.maxR = self.rs[maxRIndex]
        self.maxRX = self.xs[maxRIndex]
        self.maxRY = self.ys[maxRIndex]

        maxDrillSize = 0.1 * 2.54
        minDrillSize = 0.006 * 2.54

        self.drills = []
        self.cutouts = []

        # Largest drill is 0.1 in
        # Similarly cutout tool diameter is 0.1 in
        # Do some pruning into drills/mechanical routing steps
        for r, x, y in zip(self.rs, self.xs, self.ys):
            print(r, x, y)
            if r < minDrillSize:
                continue
            if r > maxDrillSize:
                self.cutouts.append((r, x, y))
            else:
                self.drills.append((r, x, y))

        # Just fill the trace everywhere
        # MRG TODO: possibly skip mask.
        for side, layerName in itertools.product(["Top", "Bottom"], ["Layer", "Mask"]):
            self.setLayerArtist(side, layerName, self.fillCircle)

        self.setLayerArtist("Drill", "Drill", self.drawDrills)
        self.setLayerArtist("Mech", "Mech", self.drawCutouts)

    def fillCircle(self, gerberWriter):
        gerberWriter.circle(self.maxRX, self.maxRY, self.maxR)

    def drawDrills(self, drillWriter):
        for r, x, y in self.drills:
            drillWriter.addHole(x, y, r * 2)

    def drawCutouts(self, gerberWriter):
        gerberWriter.circle(self.maxRX, self.maxRY, self.maxR)

        for r, x, y in self.cutouts:
            gerberWriter.circle(x, y, r)

if __name__ == "__main__":
    app = AppolonianTest(1)

    pcb = PCBDrawer("appotest")
    pcb.addFeature(app)
    pcb.finalize()
    pcb.visualize()
