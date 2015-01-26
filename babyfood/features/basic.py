class CenteredRectangle:
    def __init__(self, w, h):
        assert w > 0
        assert h > 0
        self._hw = w / 2
        self._hh = h / 2

    def draw(self, ctx):
        ctx.moveTo(-self._hw, self._hh)

        ctx.lineTo(self._hw, self._hh)
        ctx.lineTo(self._hw, -self._hh)
        ctx.lineTo(-self._hw, -self._hh)
        ctx.lineTo(-self._hw, self._hh)


class FilledCenteredRectangle(CenteredRectangle):
    def draw(self, ctx):
        with ctx.polygonMode():
            CenteredRectangle.draw(self, ctx)


class FilledCenteredCircle:
    def __init__(self, r):
        assert r > 0
        self._r = r

    def draw(self, ctx):
        with ctx.polygonMode():
            ctx.circle(0, 0, self._r)


class CircularVia:
    def __init__(self, padRadius, holeRadius):
        assert padRadius > 0
        assert holeRadius > 0
        assert padRadius > holeRadius
        self._pr = padRadius
        self._hr = holeRadius

    def draw(self, ctx):
        # Draw the pad on copper and overlay layers
        fcc = FilledCenteredCircle(self._pr)
        for side in ("top", "bottom"):
            ctx.setActiveSide(side)
            for layer in ("mask", "copper"):
                ctx.setActiveLayer(layer)
                fcc.draw(ctx)
        # Drill the hole
        ctx.addHole(0, 0, self._hr)
