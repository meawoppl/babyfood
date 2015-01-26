import numpy as np

from babyfood.layers.GerberLayer import GerberLayer
from babyfood.tests.shared import GerbvTester, _quickTempFilePath


class GerberLayerTestCase(GerbvTester):
    def test_gerberlayer_flash(self):
        gerbFilePath = _quickTempFilePath(".gbr")
        gw = GerberLayer(gerbFilePath)
        gw.defineCircularAperature(0.1)
        for c in [-5, 0, 5]:
            gw.flashAt(c, c)
        gw.finalize()

        self._check_gerber_file(gerbFilePath)

    def test_gerberlayer_line(self):
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

    def test_gerberlayer_arc(self):
        gerbFilePath = _quickTempFilePath(".gbr")
        gw = GerberLayer(gerbFilePath)
        gw.defineCircularAperature(0.001)

        gw.moveTo(1, 0)
        gw.arcLineTo(0, 1, 0, 0, "CW")

        gw.defineCircularAperature(0.1)
        gw.arcLineTo(-1, 0, 0, 0, "CW")

        gw.finalize()
        self._check_gerber_file(gerbFilePath)

    def test_gerberlayer_polygon(self):
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

    def test_gerberlayer_circle(self):
        gerbFilePath = _quickTempFilePath(".gbr")
        gw = GerberLayer(gerbFilePath)
        gw.defineCircularAperature(0.001)

        gw.filledCircle(0, 0, 5)
        gw.finalize()

        self._check_gerber_file(gerbFilePath)

    def test_gerberlayer_aperatures(self):
        gerbFilePath = _quickTempFilePath(".gbr")
        gw = GerberLayer(gerbFilePath)

        for n, hole in enumerate([(), (0.25,), (0.25, 0.25)]):
            x = n - 1
            gw.defineCircularAperature(0.5, hole=hole)
            gw.flashAt(x, -1)

            gw.defineRectangularAperature(0.5, 0.5, hole=hole)
            gw.flashAt(x, 0)

            gw.defineObroundAperature(0.75, 0.35, hole=hole)
            gw.flashAt(x, 1)

        gw.finalize()

        count = self._count_objects_in_file(gerbFilePath)
        self.assertEqual(count, 9)
