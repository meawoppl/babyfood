import os

from babyfood.pcb.PCBBase import PCBArtist

_layerTupleToExtension = {("top", "overlay"): "GTO",
                          ("top", "mask"): "GTS",
                          ("top", "copper"): "GTL",
                          ("bottom", "copper"): "GBL",
                          ("bottom", "mask"): "GBS",
                          ("bottom", "overlay"): "GBO",
                          (None, "outline"): "GKO"}


class OSHParkPCB(PCBArtist):
    def __init__(self, folderPath):
        PCBArtist.__init__(self)
        # Save the target output directory
        self.folderPath = folderPath

        # Make the directory if necessary
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)

        # Initialize the gerber layers
        for (layerSide, layerName), path in self._iterateFilePaths():
            self.initializeGBRLayer(path, layerName, layerSide)

        pth = os.path.join(self.folderPath, "drill.xln")
        self.initializeXLNLayer(pth)

    def _tupleToFilename(self, layerSide, layerName):
        ext = _layerTupleToExtension[(layerSide, layerName)]
        if layerSide is not None:
            name = layerSide + "_" + layerName + "." + ext
        else:
            name = layerName + "." + ext
        return os.path.join(self.folderPath, name)

    def getCurrentLayerFilePath(self):
        aSide = self.getActiveSide()
        aLayer = self.getActiveLayer()
        return self._tupleToFilename(aSide, aLayer)

    def _iterateFilePaths(self):
        for (layerSide, layerName) in _layerTupleToExtension.keys():
            path = self._tupleToFilename(layerSide, layerName)
            yield (layerSide, layerName), path

    def hintedCircle(self, cX, cY, r, n=50):
        import numpy as np
        self.circle(cX, cY, r)
        self.writeComment("Begin Circle Hints.  Can be safely ignored")
        self.defineCircularAperature(0.001)
        for theta in np.linspace(0, 2 * np.pi, n)[:-1]:
            xP = cX + np.cos(theta) * r
            yP = cY + np.sin(theta) * r
            self.flashAt(xP, yP)
        self.writeComment("End Circle Hints.")

    def visualize(self):
        # The below colorscheme is pretty similar to altium/eagles defaults
        extensionToColor = {"GTL": "#FF0000", "GBL": "#0000FF",
                            "GTO": "#FFFF00", "GBO": "#AEB404",
                            "GTS": "#DF01D7", "GBS": "#DF01D7",
                            "GKO": "#D72424"}

        filenames = []
        colors = []
        for (layerSide, layerName), path in self._iterateFilePaths():
            filenames.append(path)
            _, ext = os.path.splitext(path)
            colors.append(extensionToColor[ext[1:]])

        # Add the drill file
        colors.append("#EEEEEE")
        pth = os.path.join(self.folderPath, "drill.xln")
        filenames.append(pth)

        colorString = ""
        for c in colors:
            colorString += "--foreground=" + c + " "

        filestring = " ".join(filenames)
        gerbCallString = "gerbv " + colorString + " " + filestring

        print(gerbCallString)
        os.system(gerbCallString)
