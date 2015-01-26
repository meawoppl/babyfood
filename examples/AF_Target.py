from __future__ import division


from babyfood.pcb.OSHParkPCB import OSHParkPCB
from babyfood.pcb.PCBUnits import inch


def drawRectangle(pcb, xL, yL):
    pcb.defineRectangularAperature(xL, yL)
    pcb.flashAt(0, 0)

# Draw board outline
pcb = OSHParkPCB("aft")
pcb.setActiveLayer("outline")
pcb.defineCircularAperature(0)
h = 0.5 * inch
pcb.moveTo(h, h)
pcb.lineTo(h, -h)
pcb.lineTo(-h, -h)
pcb.lineTo(-h, h)
pcb.lineTo(h, h)


for side in ("top", "bottom"):
    for layer in ("copper", "mask", "overlay"):
        pcb.setActiveLayer(layer, side)
        drawRectangle(pcb, 0.5, 0.5)

pcb.finalize()

# pcb.setActiveLayer("overlay")




# class TargetPatch(SingleLayerFeature):
#   def __init__(self, layerTuple, size=1, grating="F"):
#       SingleLayerFeature.__init__(self, layerTuple)
#       assert grating in "FHV", "Grating code must be (H)orizontal/(V)ertical/(F)illed"
#       self.g = grating
#       self.s = size

#   def artist(self, gerberWriter):
#       xC, yC = self.transform(0, 0)

#       if self.g == "F":
#           xs, ys = self._computeRectPoly(xC, yC, self.s, self.s)
#           gerberWriter.simplePolygon(xs, ys)
#           return

#       for offset in [-2/5, 0, 2/5]:
#           if self.g == "H":
#               xC, yC = self.transform(offset, 0)
#               xs, ys = self._computeRectPoly(xC, yC, 1/5, 1)
#               gerberWriter.simplePolygon(xs, ys)
#           elif self.g == "V":
#               xC, yC = self.transform(0, offset)
#               xs, ys = self._computeRectPoly(xC, yC, 1, 1/5)
#               gerberWriter.simplePolygon(xs, ys)

#   def _computeRectPoly(self, xC, yC, w, h):
#       hw = w / 2
#       hh = h / 2
#       pts = [(xC - hw, yC + hh),
#              (xC + hw, yC + hh),
#              (xC + hw, yC - hh),
#              (xC - hw, yC - hh),
#              (xC - hw, yC + hh)]
#       print(np.array(pts).shape)
#       return np.array(pts).squeeze().T


# class TargetQuad(PCBFeature):
#   def __init__(self, layerTuple):
#       PCBFeature.__init__(self)
#       side, layer = layerTuple
#       self.setLayerArtist(side, layer, self.addPatches)
#       self.lt = layerTuple

#   def addPatches(self, gerberWriter):
#       for n, orientation in enumerate("FHV"):
#           tp = TargetPatch(self.lt, 1, orientation)
#           tp.setCentroid(n * 2, 0)
#           tp.artist(gerberWriter)

# if __name__ == "__main__":
#   from PCBBase import PCBDrawer

#   tq = TargetQuad(("Top", "Overlay"))
#   pcb = PCBDrawer("aft")
#   pcb.addFeature(tq)
#   pcb.finalize()
#   pcb.visualize()
