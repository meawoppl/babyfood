import os

from babyfood.pcb.PCBBase import PCBArtist


class OSHParkPCB(PCBArtist):
    def __init__(self, folderPath):
        PCBArtist.__init__(self)
        # Save the target output directory
        self.folderPath = folderPath

        # Make the directory if necessary
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)

        # Initialize the gerber layers
        for (layerSide, layerName), path, ext in self._iterateFilePaths():
            self.initializeGBRLayer(path, layerName, layerSide)

        pth = os.path.join(self.folderPath, "drill.xln")
        self.initializeXLNLayer(pth)

    def _iterateFilePaths(self):
        layerTupleToExtension = {("top", "overlay"): "GTO",
                                 ("top", "mask"): "GTS",
                                 ("top", "copper"): "GTL",
                                 ("bottom", "copper"): "GBL",
                                 ("bottom", "mask"): "GBS",
                                 ("bottom", "overlay"): "GBO",
                                 (None, "outline"): "GKO"}

        for (layerSide, layerName), ext in layerTupleToExtension.items():
            if layerSide:
                name = layerSide + "_" + layerName + "." + ext
            else:
                name = layerName + "." + ext
            path = os.path.join(self.folderPath, name)
            yield (layerSide, layerName), path, ext

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
        # The below colorscheme is pretty similar to altium's defaults
        extensionToColor = {"GTL": "#FF0000", "GBL": "#0000FF",
                            "GTO": "#FFFF00", "GBO": "#AEB404",
                            "GTS": "#DF01D7", "GBS": "#DF01D7",
                            "GKO": "#D72424"}

        filenames = []
        colors = []
        for (layerSide, layerName), path, ext in self._iterateFilePaths():
            filenames.append(path)
            colors.append(extensionToColor[ext])

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
