from babyfood.homogenous import TransformationContext
from babyfood.layers.GerberLayer import GerberLayer
from babyfood.layers.DrillLayer import DrillLayer


class PCBArtist:
    def __init__(self):
        self.activeSide = None
        self.activeLayer = None
        self.layerArtists = {}
        self.transform = TransformationContext()

    def _constructLayerTuple(self, layerName, layerSide=None):
        if layerSide is None:
            return (layerName,)
        return (layerSide, layerName)

    def _getLayerArtist(self, layerName, layerSide=None):
        lt = self._constructLayerTuple(layerName, layerSide)
        assert lt in self.layerArtists, "There is no layer named: " + layerName
        assert (layerSide in ["", None, "top", "bottom"])
        return self.layerArtists[lt]

    def _addLayerArtist(self, artist, layerName, layerSide=None):
        # Tie the artist matrix into ours
        artist.setTransformMatrix(self.transform.getMatrix())

        # Add it to the list of layers we can draw into
        lt = self._constructLayerTuple(layerName, layerSide)
        self.layerArtists[lt] = artist

    def initializeGBRLayer(self, pathOrFLO, layerName, layerSide=None):
        # Init the gerber writer, and add it
        gw = GerberLayer(pathOrFLO)
        self._addLayerArtist(gw, layerName, layerSide)

    def initializeXLNLayer(self, pathOrFLO, layerName):
        # Add the drill writer also
        dw = DrillLayer(pathOrFLO)
        self._addLayerArtist(dw, layerName)

        # Bind addHole so we don't need to switch to the drill layer to add holes
        self.addHole = dw.addHole

    def setActiveLayer(self, layerName, side=None):
        # Let the user set both simultaneously
        if side is not None:
            self.setActiveSide(side)

        # Look for a layer matching this name on this side
        self.activeLayer = self._getLayerArtist(layerName, self.activeSide)

    def setActiveSide(self, sideName):
        sideName = sideName.lower()
        assert sideName in ["top", "bottom"]
        self.activeSide = sideName

    def finalize(self):
        for layerArtist in self.layerArtists.values():
            layerArtist.finalize()

    # MRG NOTE: Override __dir__ similarly?
    def __getattr__(self, attrName):
        if hasattr(self.activeLayer, attrName):
            return getattr(self.activeLayer, attrName)

        # MRG TODO: Add check for drill funcitons here
        raise AttributeError
