import numpy as np
from PCBBase import PCBFeature, PCBDrawer

import itertools


def hintedCircle(gw, cX, cY, r):
    gw.defineCircularAperature(0.1, True)
    gw.circle(cX, cY, r)
    gw.writeComment("Begin Circle Hints.  Can be safely ignored")
    for theta in np.linspace(0, 2 * np.pi, 50)[:-1]:
        xP = cX + np.cos(theta) * r
        yP = cY + np.sin(theta) * r
        gw.flashAt(xP, yP)
    gw.writeComment("End Circle Hints.")


def cisDegree(angleInDeg, r=1):
    x = np.cos((np.pi / 180) * angleInDeg) * r
    y = np.sin((np.pi / 180) * angleInDeg) * r
    return x, y


class AppolonianTest(PCBFeature):
    def __init__(self, scalar):
        PCBFeature.__init__(self)

        self.rs, self.xs, self.ys = np.loadtxt("gasket.csv", skiprows=1, delimiter=",").T / scalar

        # Radaii can be negative (which does make sense really!)
        self.rs = np.abs(self.rs)

        # Find the biggest circle
        maxR = self.rs.max()

        # Rescale everything to mave a max diameter of 3in
        rescalar = (scalar * 25.4) / (2 * maxR)
        self.rs *= rescalar
        self.xs *= rescalar
        self.ys *= rescalar

        self.rs -= 0.05 * 2.54

        maxRIndex = self.rs.argmax()
        self.maxR = self.rs[maxRIndex]
        self.maxRX = self.xs[maxRIndex]
        self.maxRY = self.ys[maxRIndex]

        maxDrillSize = 0.260 * 25.4
        minDrillSize = 0.006 * 25.4

        self.drills = []
        self.cutouts = []

        # Largest drill is 0.1 in
        # Similarly cutout tool diameter is 0.1 in
        # Do some pruning into drills/mechanical routing steps
        for r, x, y in zip(self.rs, self.xs, self.ys):
            if r == self.maxR:
                print("Skipped max R")
                continue
            if r < minDrillSize:
                continue
            if r > maxDrillSize:
                self.cutouts.append((r, x, y))
            else:
                self.drills.append((r, x, y))

        # Just fill the trace everywhere
        # MRG TODO: possibly skip mask.
        for side, layerName in itertools.product(["Top", "Bottom"], ["Layer"]):
            self.setLayerArtist(side, layerName, self.fillCircle)

        self.setLayerArtist("Top", "Overlay", self.drawNullCircle)
        self.setLayerArtist("Bottom", "Overlay", self.drawNullCircle)
        self.setLayerArtist("Top", "Mask", self.drawNullCircle)

        self.setLayerArtist("Bottom", "Mask", self.fillCircle)
        self.setLayerArtist("Drill", "Drill", self.drawDrills)
        self.setLayerArtist("Mech", "Mech", self.drawCutouts)

    # def computeAttachSegs(self, segCount=7):
    #     phis = np.linspace(0, 2 * np.pi, segCount * 2 + 1)[:-1]

    def drawNullCircle(self, gerberWriter):
        gerberWriter.defineCircularAperature(1, True)
        for r, x, y in self.cutouts:
            hintedCircle(gerberWriter, x, y, r / 10)

    def fillCircle(self, gerberWriter):
        x, y, r = self.maxRX, self.maxRY, self.maxR * 1.05
        hintedCircle(gerberWriter, x, y, r)
        gerberWriter.filledCircle(x, y, r)

        # gerberWriter.circle(self.maxRX, self.maxRY, self.maxR * 1.05)

    def drawDrills(self, drillWriter):
        for r, x, y in self.drills:
            drillWriter.addHole(x, y, r * 2)

    def drawCutouts(self, gerberWriter):
        hintedCircle(gerberWriter, self.maxRX, self.maxRY, self.maxR * 1.05)

        for r, x, y in self.cutouts:
            hintedCircle(gerberWriter, x, y, r * 0.95)
            #gerberWriter.circle(x, y, r * 0.95)

        #    self.labelCutOut(gerberWriter, x, y)

    def labelCutOut(self, gerberWriter, xCenter, yCenter):
        gerberWriter.defineCircularAperature(0.01, True)
        fontRadius = 1
        centOffs = 1.25

        cCenterX = xCenter - centOffs
        cCenterY = yCenter

        oCenterX = xCenter + centOffs
        oCenterY = yCenter

        cSX, cSY = cisDegree(30, fontRadius)
        cEX, cEY = cisDegree(330, fontRadius)

        gerberWriter.moveTo(cCenterX + cSX, cSY)
        gerberWriter.arcLineTo(cCenterX + cEX, cEY, cCenterX, cCenterY, "CCW")

        gerberWriter.circle(oCenterX, oCenterY, fontRadius)

if __name__ == "__main__":
    app = AppolonianTest(2)

    pcb = PCBDrawer("appotest")
    pcb.addFeature(app)
    pcb.finalize()
    pcb.visualize()
