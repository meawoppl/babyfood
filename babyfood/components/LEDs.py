import math


# NB  From older format.  Very broken at present
class ThroughHoleLED:
    def __init__(self):
        pass

    def computePadCenters(self):
        ccSpacing = 2.54
        xs = [-ccSpacing / 2, -ccSpacing / 2]
        ys = [0, 0]
        return self.transform(xs, ys)

    def drawLayer(self, gerberWriter, size):
        gerberWriter.defineAperature(size, True)
        for px, py in self.computePadCenters():
            gerberWriter.flashAt(px, py)

    def drawTopLayer(self, gerberWriter):
        self.drawLayer(gerberWriter, 1.1 / 2)

    def drawBottomLayer(self, gerberWriter):
        self.drawLayer(gerberWriter, 1.1 / 2)

    def drawTopMask(self, gerberWriter):
        self.drawLayer(gerberWriter, 1.0 / 2)

    def drawBottomMask(self, gerberWriter):
        self.drawLayer(gerberWriter, 1.0 / 2)

    def drawDrills(self, drillWriter):
        for px, py in self.computePadCenters():
            drillWriter.addHole(px, py, 0.5 * math.sqrt(2) + 0.15)
