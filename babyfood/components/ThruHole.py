# http://www.mouser.com/ProductDetail/STMicroelectronics/15KE220CA/?qs=M848ylJt4n3ayMKA%2F4Jjvw%3D%3D

from babyfood.pcb.PCBUnits import toMM
from babyfood.features.basic import CircularVia, CenteredRectangle
from babyfood.components.ABC import AbstractTHComponent


class THTwoLead(AbstractTHComponent):
    def __init__(self, centerToCenter, padD, viaD):
        self._cc = centerToCenter
        self._vd = viaD
        self._pd = padD

        assert self._vd < self._pd, "Hole/Pad sizing seems wonky"

        AbstractTHComponent.__init__(self)

    def draw(self, ctx):
        # Pinz
        pin = CircularVia(toMM(self._pd) / 2, toMM(self._vd) / 2)

        dx = self._cc / 2
        for x in [-dx, dx]:
            with ctx.transform.translation(x, 0):
                pin.draw(ctx)

        # Outline
        ctx.setActiveLayer("overlay")
        re = CenteredRectangle(toMM(9.5), toMM(5))
        re.draw(ctx)


class THDiode(THTwoLead):
    pass


class ST_15KE(THDiode):
    def __init__(self):
        THTwoLead.__init__(self, toMM(15), toMM(3), toMM(1.25))


class ST_15KE22CA(ST_15KE):
    pass


class ST_15KE220CA(ST_15KE):
    pass
