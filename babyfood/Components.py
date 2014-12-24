import numpy as np
from PCBBase import PCBDrawer, PCBFeature


# From https://www.digikey.com/Web%20Export/Supplier%20Content/Vishay_8026/PDF/VishayBeyschlag_SolderPad.pdf?redirected=1
resistorsParams = {
    "0102": (0.65, 1.10, 1.40, 2.85),
    "0204": (1.50, 1.25, 1.75, 4.00),
    "0207": (2.80, 2.20, 2.20, 7.20),
    "0402": (0.25, 0.60, 0.55, 1.45),
    "0603": (0.50, 0.95, 0.95, 2.40),
    "0805": (0.65, 1.10, 1.40, 2.85),
    "1206": (1.50, 1.25, 1.75, 4.00)}


class StdSMAResistor(PCBFeature):
    def __init__(self, codeString):
        PCBFeature.__init__(self)
        # MRG TODO: MM assertion
        self._g, self._y, self._x, self._z = resistorsParams[codeString]

        self.width = int(codeString[0:2]) * 0.254
        self.height = int(codeString[2:4]) * 0.254

        self.setLayerArtist("Top", "Mask", self.drawTopMask)
        self.setLayerArtist("Top", "Layer", self.drawTopLayer)

    def _computePadCoords(self, buff=0):
        x1 = (self._g / 2) - buff
        x2 = (self._z / 2) + buff

        y1 = (-self._x / 2) - buff
        y2 = (self._x / 2) + buff

        coords = []
        coords.append((x1, y1))
        coords.append((x1, y2))
        coords.append((x2, y2))
        coords.append((x2, y1))
        coords.append((x1, y1))
        return np.array(coords).T

    def drawTopMask(self, gerberWriter):
        xs1, ys1 = self._computePadCoords(buff=0)
        # Pad two is just mirrored wrt to y-axis
        xs2, ys2 = -xs1.copy(), ys1.copy()

        xs1, ys1 = self.transform(xs1, ys1)
        xs2, ys2 = self.transform(xs2, ys2)

        gerberWriter.simplePolygon(xs1, ys1)
        gerberWriter.simplePolygon(xs2, ys2)

    def drawTopLayer(self, gerberWriter):
        xs1, ys1 = self._computePadCoords(buff=0.1)
        # Pad two is just mirrored wrt to y-axis
        xs2, ys2 = -xs1.copy(), ys1.copy()

        xs1, ys1 = self.transform(xs1, ys1)
        xs2, ys2 = self.transform(xs2, ys2)

        gerberWriter.simplePolygon(xs1, ys1)
        gerberWriter.simplePolygon(xs2, ys2)


class ThroughHoleLED(PCBFeature):
    def __init__(self):
        PCBFeature.__init__(self)
        self.setLayerArtist("Top", "Layer", self.drawTopLayer)
        self.setLayerArtist("Top", "Mask", self.drawTopMask)
        self.setLayerArtist("Bottom", "Layer", self.drawBottomLayer)
        self.setLayerArtist("Bottom", "Mask", self.drawBottomMask)
        self.setLayerArtist("Drill", "Drill", self.drawDrills)

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
            drillWriter.addHole(px, py, 0.5 * np.sqrt(2) + 0.15)


class TraceSegment(PCBFeature):
    def __init__(self, sPt, ePt, width):
        PCBFeature.__init__(self)
        self.sPt = sPt
        self.ePt = ePt
        self.w = width

    def drawSegment(self, gerberWriter):
        gerberWriter.defineAperature(self.w, setAsCurrent=True)
        gerberWriter.moveTo(self.transform(self.sPt))
        gerberWriter.lineTo(self.transform(self.ePt))


class TestFeature(PCBFeature):
    def __init__(self):
        PCBFeature.__init__(self)

        ts = np.linspace(0, 2 * np.pi, 7)[:-1]
        xs = np.cos(ts) * 3
        ys = np.sin(ts) * 3

        self.setLayerArtist("Top", "Mask", self.drawTriFactory(xs[0], ys[0], 2))
        self.setLayerArtist("Top", "Layer", self.drawTriFactory(xs[1], ys[1], 2))
        self.setLayerArtist("Top", "Overlay", self.drawTriFactory(xs[2], ys[2], 2))

        self.setLayerArtist("Bottom", "Mask", self.drawTriFactory(xs[3], ys[3], 2))
        self.setLayerArtist("Bottom", "Layer", self.drawTriFactory(xs[4], ys[4], 2))
        self.setLayerArtist("Bottom", "Overlay", self.drawTriFactory(xs[5], ys[5], 2))

        self.setLayerArtist("Drill", "Drill", self.drawDrills)

    def drawTriFactory(self, x, y, s):
        def tDraw(gWrit):
            ts = np.linspace(0, 2 * np.pi, 4)
            xs = (np.cos(ts) * s) + x
            ys = (np.sin(ts) * s) + y
            gWrit.simplePolygon(xs, ys)
            gWrit.defineAperature(0.1, True)
            gWrit.circle(x, y, s)
        return tDraw

    def drawDrills(self, drillWriter):
        ts = np.linspace(0, 2 * np.pi, 7)[:-1]
        xs = np.cos(ts) * 3
        ys = np.sin(ts) * 3

        for px, py in zip(xs, ys):
            drillWriter.addHole(px, py, 0.5 * np.sqrt(2) + 0.15)


if __name__ == "__main__":
    pcb = PCBDrawer("testing")
    # r1 = ThroughHoleLED()
    # r1.setRotation(np.pi / 7)

    # pcb.addFeature(r1)

    # r2 = StdSMAResistor("0805")
    # for phi in range(5):
    #     r2.setCentroid(0, -7 + 3 * phi)
    #     pcb.addFeature(r2)

    pcb.addFeature(TestFeature())

    extent = 5.1
    pcb.drawOutline((-extent, -extent), (extent, extent))
    pcb.finalize()
    pcb.visualize()
