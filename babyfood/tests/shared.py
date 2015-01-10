import os, random, subprocess, tempfile, unittest

from PIL import Image

import numpy as np


# Just see if gerbv is alive and kicking
_gerbvTestCall = ("gerbv", "-V")

# Call with 100dpi, and no border
_gerbvCalibratedCall = ("gerbv", "--dpi=1024", "--border=0")


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


class GerbvTester(unittest.TestCase):
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
        else:
            os.remove(txtTrace)

        self.assertTrue(os.path.exists(pngPath))

        # gerbv made it through.  next check the output file is a valid png
        pngData = patched_imread(pngPath)

        if flatten:
            pngData = pngData.sum(axis=2) / 3

        print(pngData.shape)
        self.assertTrue(pngData.shape > (1, 1))

        return pngData
