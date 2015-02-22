# import numpy as np
# from babyfood import PCBDrawer, PCBFeature
# class TraceSegment(PCBFeature):
#     def __init__(self, sPt, ePt, width):
#         PCBFeature.__init__(self)
#         self.sPt = sPt
#         self.ePt = ePt
#         self.w = width

#     def drawSegment(self, gerberWriter):
#         gerberWriter.defineAperature(self.w, setAsCurrent=True)
#         gerberWriter.moveTo(self.transform(self.sPt))
#         gerberWriter.lineTo(self.transform(self.ePt))


# class TestFeature(PCBFeature):
#     def __init__(self):
#         PCBFeature.__init__(self)

#         ts = np.linspace(0, 2 * np.pi, 7)[:-1]
#         xs = np.cos(ts) * 3
#         ys = np.sin(ts) * 3

#         self.setLayerArtist("Top", "Mask", self.drawTriFactory(xs[0], ys[0], 2))
#         self.setLayerArtist("Top", "Layer", self.drawTriFactory(xs[1], ys[1], 2))
#         self.setLayerArtist("Top", "Overlay", self.drawTriFactory(xs[2], ys[2], 2))

#         self.setLayerArtist("Bottom", "Mask", self.drawTriFactory(xs[3], ys[3], 2))
#         self.setLayerArtist("Bottom", "Layer", self.drawTriFactory(xs[4], ys[4], 2))
#         self.setLayerArtist("Bottom", "Overlay", self.drawTriFactory(xs[5], ys[5], 2))

#         self.setLayerArtist("Drill", "Drill", self.drawDrills)

#     def drawTriFactory(self, x, y, s):
#         def tDraw(gWrit):
#             ts = np.linspace(0, 2 * np.pi, 4)
#             xs = (np.cos(ts) * s) + x
#             ys = (np.sin(ts) * s) + y
#             gWrit.simplePolygon(xs, ys)
#             gWrit.defineAperature(0.1, True)
#             gWrit.circle(x, y, s)
#         return tDraw

#     def drawDrills(self, drillWriter):
#         ts = np.linspace(0, 2 * np.pi, 7)[:-1]
#         xs = np.cos(ts) * 3
#         ys = np.sin(ts) * 3

#         for px, py in zip(xs, ys):
#             drillWriter.addHole(px, py, 0.5 * np.sqrt(2) + 0.15)


# if __name__ == "__main__":
#     pcb = PCBDrawer("testing")
#     # r1 = ThroughHoleLED()
#     # r1.setRotation(np.pi / 7)

#     # pcb.addFeature(r1)

#     # r2 = StdSMAResistor("0805")
#     # for phi in range(5):
#     #     r2.setCentroid(0, -7 + 3 * phi)
#     #     pcb.addFeature(r2)

#     pcb.addFeature(TestFeature())

#     extent = 5.1
#     pcb.drawOutline((-extent, -extent), (extent, extent))
#     pcb.finalize()
#     pcb.visualize()
