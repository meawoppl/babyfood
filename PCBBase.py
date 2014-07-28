import os
import numpy as np

from GerberWriter import GerberWriter
from DrillWriter import DrillWriter


class PCBFeature:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.phi = 0

    def setCentroid(self, x, y):
        self.x = x
        self.y = y

    def setRotation(self, phi):
        self.phi = phi

    def transform(self, xs, ys):
        p = self.phi
        m = np.matrix([[np.cos(p), -np.sin(p)],
                       [np.sin(p), np.cos(p)]])
        print("xy", xs, ys)
        lhs = np.c_[xs, ys].T

        print(m.shape, lhs.shape)
        txs, tys = m * lhs
        return np.array(txs + self.x).flatten(), np.array(tys + self.y).flatten()

    def drawTopOverlay(self, gerberWriter):
        pass

    def drawTopMask(self, gerberWriter):
        pass

    def drawTopLayer(self, gerberWriter):
        pass

    def drawBottomLayer(self, gerberWriter):
        pass

    def drawBottomMask(self, gerberWriter):
        pass

    def drawBottomOverlay(self, gerberWriter):
        pass

    def drawDrills(self, drillFileWriter):
        pass


class SingleSideComponent(PCBFeature):
    pass


class TopSideFeature(SingleSideComponent):
    pass


class BottomSideFeature(SingleSideComponent):
    pass


class DualSideSymmFeature(PCBFeature):
    pass


class DualSideAsymFeature(PCBFeature):
    pass


nameToExtension = {"TopOverlay": "GTO", "TopMask": "GTS", "TopLayer": "GTL",
                   "BottomLayer": "GBL", "BottomMask": "GBS", "BottomOverlay": "GBO"}


extensionToColor = {"GTL": "#FF0000", "GBL": "#0000FF",
                    "GTO": "#FFFF00", "GBO": "#AEB404",
                    "GTS": "#DF01D7", "GBS": "#DF01D7"}


class PCBDrawer:
    def __init__(self, folderPath, filename="pcb"):
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)

        self.pth = os.path.join(folderPath, filename)
        self.layerWriters = {}
        for name, ext in nameToExtension.items():
            gw = GerberWriter(self.pth + "." + ext)
            gw.writeGerberHeader()
            gw.writeLayerPolarity("C" if "Mask" in name else "D")
            self.layerWriters[name] = gw

        self.drillWriter = DrillWriter(folderPath + ".drl")

    def addFeature(self, pcbFeature):
        for layerName, layerWriter in self.layerWriters.items():
            getattr(pcbFeature, "draw" + layerName)(layerWriter)

        pcbFeature.drawDrills(self.drillWriter)

    def finalize(self):
        for layerWriter in self.layerWriters.values():
            layerWriter.finalize()

        self.drillWriter.finalize()

    def visualize(self):
        filenames = []
        colors = []
        for ext, code in extensionToColor.items():
            filenames.append(self.pth + "." + ext)
            colors.append(code)

        # Add the drill file
        colors.append("#EEEEEE")
        filenames.append(self.pth + ".drl")

        colorString = ""
        for c in colors:
            colorString += "--foreground=" + c + " "

        filestring = " ".join(filenames)
        gerbCallString = "gerbv " + colorString + " " + filestring
        print(gerbCallString)
        os.system(gerbCallString)

# From https://www.digikey.com/Web%20Export/Supplier%20Content/Vishay_8026/PDF/VishayBeyschlag_SolderPad.pdf?redirected=1

resistorsParams = {
    "0102": (0.65, 1.10, 1.40, 2.85),
    "0204": (1.50, 1.25, 1.75, 4.00),
    "0207": (2.80, 2.20, 2.20, 7.20),
    "0402": (0.25, 0.60, 0.55, 1.45),
    "0603": (0.50, 0.95, 0.95, 2.40),
    "0805": (0.65, 1.10, 1.40, 2.85),
    "1206": (1.50, 1.25, 1.75, 4.00)}


class StdSMAResistor(TopSideFeature):
    def __init__(self, codeString):
        self.x = 0
        self.y = 0
        self.phi = 0

        assert codeString in resistorsParams, "Wtf ^^"
        # MRG TODO: MM assertion
        self.g, self.y, self.x, self.z = resistorsParams[codeString]

        self.width = int(codeString[0:2]) * 0.254
        self.height = int(codeString[2:4]) * 0.254

    def computePadCoords(self, buff=0):
        x1 = (self.g / 2) - buff
        x2 = (self.z / 2) + buff

        y1 = (-self.x / 2) - buff
        y2 = (self.x / 2) + buff

        coords = []
        coords.append((x1, y1))
        coords.append((x1, y2))
        coords.append((x2, y2))
        coords.append((x2, y1))
        coords.append((x1, y1))
        return np.array(coords).T

    def drawTopMask(self, gerberWriter):
        xs1, ys1 = np.array(self.computePadCoords(buff=0))
        # Pad two is just mirrored wrt to y-axis
        xs2, ys2 = -xs1.copy(), ys1.copy()

        xs1, ys1 = self.transform(xs1, ys1)
        xs2, ys2 = self.transform(xs2, ys2)

        gerberWriter.simplePolygon(xs1, ys1)
        gerberWriter.simplePolygon(xs2, ys2)

    def drawTopLayer(self, gerberWriter):
        xs1, ys1 = np.array(self.computePadCoords(buff=0.1))
        # Pad two is just mirrored wrt to y-axis
        xs2, ys2 = -xs1.copy(), ys1.copy()

        xs1, ys1 = self.transform(xs1, ys1)
        xs2, ys2 = self.transform(xs2, ys2)

        gerberWriter.simplePolygon(xs1, ys1)
        gerberWriter.simplePolygon(xs2, ys2)


if __name__ == "__main__":
    pcb = PCBDrawer("testing")
    r = StdSMAResistor("0805")
    r.setRotation(np.pi / 7)
    pcb.addFeature(r)

    pcb.finalize()
    pcb.visualize()
