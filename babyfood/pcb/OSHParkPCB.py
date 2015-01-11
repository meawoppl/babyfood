import os

from babyfood.pcb.PCBBase import PCBArtist


class OSHParkPCB(PCBArtist):
    def __init__(self, folderPath):
        PCBArtist.__init__(self)
        self.folderPath = folderPath
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)

        for (layerSide, layerName), path, ext in self._iterateFilePaths():
            pth = os.path.join(folderPath, layerSide + "_" + layerName + ext)
            self.initializeGBRLayer(pth, layerName, layerSide)

        pth = os.path.join(folderPath, "drill.xln")
        self.initializeXLNLayer(pth, "drill")

    def _iterateFilePaths(self):
        layerTupleToExtension = {("top", "overlay"): "GTO",
                                 ("top", "mask"): "GTS",
                                 ("top", "layer"): "GTL",
                                 ("bottom", "layer"): "GBL",
                                 ("bottom", "mask"): "GBS",
                                 ("bottom", "overlay"): "GBO",
                                 ("", "outline"): "GKO"}

        for (layerSide, layerName), ext in layerTupleToExtension.items():
            if layerSide:
                name = layerName + "." + ext
            else:
                name = layerName + "." + ext
            path = os.path.join(self.folderPath, name)
            yield (layerSide, layerName), path, ext

    def hintedCircle(self, pcb, cX, cY, r):
        import numpy as np
        self.defineCircularAperature(0.0, True)
        self.circle(cX, cY, r)
        self.writeComment("Begin Circle Hints.  Can be safely ignored")
        for theta in np.linspace(0, 2 * np.pi, 50)[:-1]:
            xP = cX + np.cos(theta) * r
            yP = cY + np.sin(theta) * r
            self.flashAt(xP, yP)
        self.writeComment("End Circle Hints.")

    def visualize(self):
        extensionToColor = {"GTL": "#FF0000", "GBL": "#0000FF",
                            "GTO": "#FFFF00", "GBO": "#AEB404",
                            "GTS": "#DF01D7", "GBS": "#DF01D7",
                            "GKO": "#D72424"}

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

        print(gerbCallString)
        os.system(gerbCallString)
