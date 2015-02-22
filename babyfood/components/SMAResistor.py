# From https://www.digikey.com/Web%20Export/Supplier%20Content/Vishay_8026/PDF/VishayBeyschlag_SolderPad.pdf?redirected=1

from babyfood.pcb.PCBUnits import mil
from babyfood.features.basic import CenteredRectangle, FilledCenteredRectangle
from babyfood.components.ABC import AbstractSMAComponent


resistorsParams = {
    "0102": (0.65, 1.10, 1.40, 2.85),
    "0204": (1.50, 1.25, 1.75, 4.00),
    "0207": (2.80, 2.20, 2.20, 7.20),
    "0402": (0.25, 0.60, 0.55, 1.45),
    "0603": (0.50, 0.95, 0.95, 2.40),
    "0805": (0.65, 1.10, 1.40, 2.85),
    "1206": (1.50, 1.25, 1.75, 4.00)}


class SMAResistor(AbstractSMAComponent):
    def __init__(self, codeString):
        # Names on datasheet ref'ed above
        _g, _y, _x, _z = resistorsParams[codeString]

        # Names useful to us
        self._w = _y
        self._h = _x

        shift = (_g / 2) + (_y / 2)

        self._outline = int(codeString[0:2]) * 0.254, int(codeString[2:4]) * 0.254
        print(self._outline)

        self._centers = ((-shift, 0),
                         (+shift, 0))

    def draw(self, ctx):
        pad = FilledCenteredRectangle(self._w, self._h)
        mask = FilledCenteredRectangle(self._w - 0.1, self._h - 0.1)
        outline = CenteredRectangle(*self._outline)
        ctx.setActiveLayer("overlay")
        outline.draw(ctx)

        for cp in self._centers:
            with ctx.transform.translation(*cp):
                ctx.setActiveLayer("copper")
                pad.draw(ctx)
                ctx.setActiveLayer("mask")
                mask.draw(ctx)
