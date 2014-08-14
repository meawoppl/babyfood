import itertools, os
import numpy as np

from GerberWriter import GerberWriter
from DrillWriter import DrillWriter


class TransformableFeature:
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


class PCBFeature(TransformableFeature):
    def __init__(self):
        TransformableFeature.__init__(self)
        self.artists = {}
        self.flipped = False

    def setLayerArtist(self, layerSide, layerType, artistFunc):
        self.artists[(layerSide, layerType)] = artistFunc

    def getLayerArtist(self, layerSide, layerType):
        assert layerSide in ["Top", "Bottom"]

        sideMap = self._switcher(layerSide)
        return self.artists[(sideMap, layerType)]

    def setFlip(self, flipped):
        self.flipped = flipped

    def _switcher(self, torb):
        if self.flipped:
            return {"Top": "Bottom", "Bottom": "Top"}[torb]
        else:
            return torb

boardSides = ["Top", "Bottom"]
layerTypes = ["Layer", "Mask", "Overlay"]
defaultLayers = list(itertools.product(boardSides, layerTypes))

layerTupleToExtension = {("Top", "Overlay"): "GTO",
                         ("Top", "Mask"): "GTS",
                         ("Top", "Layer"): "GTL",
                         ("Bottom", "Layer"): "GBL",
                         ("Bottom", "Mask"): "GBS",
                         ("Bottom", "Overlay"): "GBO"}


extensionToColor = {"GTL": "#FF0000", "GBL": "#0000FF",
                    "GTO": "#FFFF00", "GBO": "#AEB404",
                    "GTS": "#DF01D7", "GBS": "#DF01D7"}


class PCBDrawer:
    def __init__(self, folderPath, filename="pcb", layers=defaultLayers):
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)

        self.pth = os.path.join(folderPath, filename)
        self.layerWriters = {}
        for layerTuple, layerExt in layerTupleToExtension.items():
            gw = GerberWriter(self.pth + "." + layerExt)
            gw.writeGerberHeader()
            gw.writeLayerPolarity()
            self.layerWriters[layerTuple] = gw

        # Add also teh drill writer
        dw = DrillWriter(self.pth + ".XLN")
        self.layerWriters[("Drill", "Drill")] = dw

        self.outlined = False

    def drawOutline(self, pt1, pt2):
        x1, y1 = pt1
        x2, y2 = pt2

        gw = GerberWriter(self.pth + ".GKO")
        gw.writeGerberHeader()
        gw.writeLayerPolarity()

        gw.defineAperature(0.1, setAsCurrent=True)
        gw.moveTo(x1, y1)
        gw.lineTo(x1, y2)
        gw.lineTo(x2, y2)
        gw.lineTo(x2, y1)
        gw.lineTo(x1, y1)

        gw.finalize()

        self.outlined = True

    def addFeature(self, pcbFeature):
        for layerTuple, artist in pcbFeature.artists.items():
            artist(self.layerWriters[layerTuple])

    def finalize(self):
        for layerWriter in self.layerWriters.values():
            layerWriter.finalize()

    def visualize(self):
        filenames = []
        colors = []
        for ext, code in extensionToColor.items():
            filenames.append(self.pth + "." + ext)
            colors.append(code)

        # Add the drill file
        colors.append("#EEEEEE")
        filenames.append(self.pth + ".XLN")

        colorString = ""
        for c in colors:
            colorString += "--foreground=" + c + " "

        filestring = " ".join(filenames)
        gerbCallString = "gerbv " + colorString + " " + filestring

        if self.outlined:
            gerbCallString += " " + self.pth + ".GKO"
        print(gerbCallString)
        os.system(gerbCallString)
