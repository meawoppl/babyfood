from babyfood.homogenous import TransformationContext
from babyfood.layers.GerberLayer import GerberLayer
from babyfood.layers.DrillLayer import DrillLayer


class PCBArtist:
    def __init__(self):
        self.activeSide = None
        self.activeLayer = None
        self.layerArtists = {"top": {}, "bottom": {}, None: {}}
        self.transform = TransformationContext()

    def _sanityCheckNameSide(self, name, side):
        # Sanity check the arguments
        assert name in ["copper", "overlay", "mask", "solder", "drill", "outline"]
        assert side in [None, "top", "bottom"]
        # MRG TODO: more comprehensive when format settles
        # At presnt drill layers could be in the top bucket etc.

    def _getLayerArtist(self, layerName, layerSide):
        self._sanityCheckNameSide(layerName, layerSide)

        # Check the unsided artists first
        if layerName in self.layerArtists[None]:
            return self.layerArtists[None][layerName]

        # Check if the layer exists
        if layerName not in self.layerArtists[layerSide]:
            layerList = repr(list(self.layerArtists.keys()))
            raise RuntimeError("There is no layer named: %s in %s" % (layerName, layerList))

        # Return the layer!
        return self.layerArtists[layerSide][layerName]

    def _addLayerArtist(self, artist, layerName, layerSide):
        self._sanityCheckNameSide(layerName, layerSide)

        # Tie the artist matrix into ours
        artist.setTransformMatrix(self.transform.getMatrix())

        # Add it to the list of layers we can draw into
        self.layerArtists[layerSide][layerName] = artist

    def initializeGBRLayer(self, pathOrFLO, layerName, layerSide=None):
        # Init the gerber writer, and add it
        gw = GerberLayer(pathOrFLO)
        self._addLayerArtist(gw, layerName, layerSide)

    def initializeXLNLayer(self, pathOrFLO):
        # Add the drill writer also
        dw = DrillLayer(pathOrFLO)
        self._addLayerArtist(dw, "drill", None)

        # Bind addHole so we don't need to switch to the drill layer to add holes
        self.addHole = dw.addHole

    def getActiveLayerArtist(self):
        return self.activeLayer

    def getActiveLayer(self):
        return self.activeLayerName

    def setActiveLayer(self, layerName, side=None):
        # Let the user set both simultaneously
        if side is not None:
            self.setActiveSide(side)

        # Look for a layer matching this name on this side
        self.activeLayer = self._getLayerArtist(layerName, self.activeSide)
        self.activeLayerName = layerName

    def getActiveSide(self):
        return self.activeSide

    def setActiveSide(self, sideName):
        sideName = sideName.lower()
        assert sideName in ["top", "bottom"]
        self.activeSide = sideName

    def finalize(self):
        for sideName, layerArtists in self.layerArtists.items():
            for layerName, layerArtist in layerArtists.items():
                layerArtist.finalize()

    # MRG NOTE: Override __dir__ similarly?
    def __getattr__(self, attrName):
        if hasattr(self.activeLayer, attrName):
            return getattr(self.activeLayer, attrName)

        # MRG TODO: Add check for drill funcitons here
        raise AttributeError
