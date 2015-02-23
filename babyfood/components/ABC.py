from babyfood.homogenous import HomogenousTransform


class AbstractComponent:
    def __init__(self):
        self._connectorIDs = []
        self._connectorNames = []
        self._connectorXYs = []
        self._xform = HomogenousTransform()

    def _addConnector(self, idee, xy, name=None):
        if name is None:
            name = "Pin " + str(idee)

        # Super sanity check these ones, avoid dumb later.
        assert int(idee) == idee, "ID must be an integer"
        assert str(name) == name, "Name must be a string"
        assert len(xy) == 2
        assert float(xy[0]) == xy[0]
        assert float(xy[1]) == xy[1]

        self._connectorIDs.append(idee)
        self._connectorNames.append(name)
        self._connectorXYs.append(xy)

    def getConnectorIDs(self):
        return self._connectorIDs

    def getConnectorNames(self):
        return self._connectorNames

    def getConnectorCenters(self):
        return self._xform.project(self._connectorXYs)

    def place(self, ctx):
        self._side = ctx.getActiveSide()
        self._xform = ctx.transform.copyCurrentTransform()


class AbstractSMAComponent(AbstractComponent):
    def addPad(self, idee, xy, name=None):
        self._addConnector(idee, xy, name)


class AbstractTHComponent(AbstractComponent):
    def addPin(self, idee, xy, name=None):
        self._addConnector(idee, xy, name)
