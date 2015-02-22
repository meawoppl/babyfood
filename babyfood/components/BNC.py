# http://media.digikey.com/pdf/Data%20Sheets/Molex%20PDFs/73131-5013.pdf

from babyfood.pcb.PCBUnits import toMM
from babyfood.features.basic import CircularVia, CenteredRectangle, CenteredCircle
from babyfod.components.ABC import AbstractTHComponent


class BNC(AbstractTHComponent):
    def __init__(self):
        pass

    def draw(self, ctx):
        # Mounting holes
        mount = CircularVia(toMM(3) / 2, toMM(2) / 2)

        offset = 10.16 / 2
        with ctx.transform.translation(offset, offset):
            mount.draw(ctx)

        with ctx.transform.translation(-offset, -offset):
            mount.draw(ctx)

        # Pinz
        pin = CircularVia(toMM(1.2) / 2, toMM(0.9) / 2)
        pin.draw(ctx)

        with ctx.transform.translation(2.54, 0):
            pin.draw(ctx)

        # Outline
        ctx.setActiveLayer("overlay")
        re = CenteredRectangle(toMM(14.78), toMM(15.88))
        re.draw(ctx)

        barrel = CenteredCircle(12.83 / 2)
        barrel.draw(ctx)
