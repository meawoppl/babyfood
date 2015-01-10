import os, random, subprocess, tempfile, unittest

from PIL import Image
import numpy as np

from babyfood.layers.GerberLayer import GerberLayer

# Just see if gerbv is alive and kicking
_gerbvTestCall = ("gerbv", "-V")

# Call with 100dpi, and no border
_gerbvCalibratedCall = ("gerbv", "--dpi=100", "--border=0")


def quiet_check_call(call):
    with open(os.devnull, "wb") as devnull:
        return subprocess.check_call(call, stdout=devnull)


def patched_imread(imgPath):
    with open(imgPath, "rb") as img_file:
        with Image.open(img_file) as img:
            return np.array(img)


# MRG NB: fast, but not secure, hacky, bad. XXX
def _quickTempFilePath(suffix):
    characters = ("abcdefghijklmnopqrstuvwxyz" +
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
                  "0123456789")
    name = "".join([random.choice(characters) for c in range(10)]) + suffix
    path = os.path.join(tempfile.gettempdir(), name)
    return path


class GerberWriterTestCase(unittest.TestCase):
    def test_gerbv_exists(self):
        result = quiet_check_call(_gerbvTestCall)
        self.assertEqual(result, 0)

    def test_gerbv_version(self):
        # Make a call to get the version.
        output = subprocess.check_output(_gerbvTestCall).decode("UTF-8")

        # Parse it into a version tuple.
        versionString = output.split()[2]
        versionTuple = tuple([int(vn) for vn in versionString.split(".")])

        # Modern mint/ubunutu can d/l 2.6, but travis seems to only be up to 2.5
        newEnough = versionTuple > (2, 4, 0)
        if not newEnough:
            print("Gerbv Version:" + versionTuple)
        self.assertTrue(newEnough)

    def _check_gerber_file(self, filepath, flatten=True):
        # Stupid check #1
        self.assertTrue(os.path.exists(filepath))

        # Next, make sure it get through gerbv export
        pngPath = _quickTempFilePath(".png")
        txtTrace = _quickTempFilePath(".txt")
        gvCall = _gerbvCalibratedCall + ("-x", "png", "-o", pngPath, filepath)

        with open(txtTrace, "w") as output:
            callSuccess = subprocess.check_call(gvCall, stdout=output) == 0

        # Make sure the call succeeded, and the png was generated.
        if not callSuccess:
            print("Gerbv returned non-zero exit code.  Gerbv Trace follows")
            raise RuntimeError(open(txtTrace).read())

        self.assertTrue(os.path.exists(pngPath))

        # gerbv made it through.  next check the output file is a valid png
        pngData = patched_imread(pngPath)

        if flatten:
            pngData = pngData.sum(axis=2) / 3

        self.assertTrue(pngData.shape > (1, 1))

        return pngData

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
