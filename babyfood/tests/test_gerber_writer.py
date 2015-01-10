import numpy as np

from babyfood.layers.GerberLayer import GerberLayer
from babyfood.tests.shared import GerbvTester, _quickTempFilePath


class GerberWriterTestCase(GerbvTester):
    def test_gw_flash(self):
        gerbFilePath = _quickTempFilePath(".gbr")
        gw = GerberLayer(gerbFilePath)
        gw.defineCircularAperature(0.1)
        for c in [-5, 0, 5]:
            gw.flashAt(c, c)
        gw.finalize()

        self._check_gerber_file(gerbFilePath)

    def test_gw_line(self):
        # Generate a temp gerber file
        gerbFilePath = _quickTempFilePath(".gbr")
        gw = GerberLayer(gerbFilePath)
        gw.defineCircularAperature(0.001)
        # Draw a square.
        gw.moveTo(10, 10)
        gw.lineTo(-10, 10)
        gw.lineTo(-10, -10)
        gw.lineTo(10, -10)
        gw.lineTo(10, 10)
        gw.finalize()

        self._check_gerber_file(gerbFilePath)

    def test_gw_polygon(self):
        gerbFilePath = _quickTempFilePath(".gbr")
        gw = GerberLayer(gerbFilePath)
        gw.defineCircularAperature(0.001)

        # Make an oval
        ts = np.linspace(0, 2 * np.pi, 10)
        xs = np.cos(ts)
        ys = np.sin(ts) * 1.5

        gw.polygon(xs, ys)
        gw.finalize()

        self._check_gerber_file(gerbFilePath)

    def test_gw_circle(self):
        gerbFilePath = _quickTempFilePath(".gbr")
        gw = GerberLayer(gerbFilePath)
        gw.defineCircularAperature(0.001)

        gw.filledCircle(0, 0, 5)
        gw.finalize()

        self._check_gerber_file(gerbFilePath)

    def test_gl_aperatures(self):
        gerbFilePath = _quickTempFilePath(".gbr")
        gw = GerberLayer(gerbFilePath)

        for n, hole in enumerate([(), (0.25,), (0.25, 0.25)]):
            x = n - 1
            gw.defineCircularAperature(0.5, hole=hole)
            gw.flashAt(x, -1)

            gw.defineRectangularAperature(0.5, 0.5, hole=hole)
            gw.flashAt(x, 0)

            gw.defineObroundAperature(0.75, 0.25, hole=hole)
            gw.flashAt(x, 1)

        gw.finalize()

        self._check_gerber_file(gerbFilePath)
