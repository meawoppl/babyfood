import os, random, subprocess, tempfile, unittest

from PIL import Image

import numpy as np


# Just see if gerbv is alive and kicking
_gerbvTestCall = ("gerbv", "-V")

# Call with 1024dpi, and no border
_gerbvCalibratedCall = ("gerbv", "--dpi=1024", "--border=0", "--background=#000000", "--foreground=#FF0000")

_gerbvCalibratedCallSingle = _gerbvCalibratedCall + ("--foreground=#FF0000",)


def quiet_check_call(call):
    with open(os.devnull, "wb") as devnull:
        return subprocess.check_call(call, stdout=devnull)


def patched_imread(imgPath):
    '''
    Return a binarized image of a png.
    Everythign that is black is 0, all
    else is 1.
    '''
    with open(imgPath, "rb") as img_file:
        with Image.open(img_file) as img:
            img = np.array(img)
            if img.ndim == 3:
                img = (img.sum(axis=2) / 3).astype(np.uint8)
            return 1 * (img != 0)


# MRG NB: fast, but not secure, hacky, bad. XXX
def _quickTempFilePath(suffix=""):
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

    def _call_gerbv_on_files(self, fileList):
        assert len(fileList) > 0

        # Specify the foreground to be the same color for all layers
        pngPath = _quickTempFilePath(".png")
        gerbvMultiCall = _gerbvCalibratedCall + ("--foreground=#FF0000",) * len(fileList)
        gerbvMultiCall = gerbvMultiCall + ("-x", "png", "-o", pngPath) + tuple(fileList)

        txtTrace = _quickTempFilePath(".txt")
        with open(txtTrace, "w") as output:
            callSuccess = subprocess.check_call(gerbvMultiCall, stdout=output) == 0

        if not callSuccess:
            print("Gerbv returned non-zero exit code.  Gerbv Trace follows")
            raise RuntimeError(open(txtTrace).read())
        else:
            os.remove(txtTrace)

        self.assertTrue(os.path.exists(pngPath))
        return pngPath

    def _check_gerber_file(self, filepath):
        '''
        This call check gerber and excillon drill files
        it makes a call to gerbv to convert the file into
        a png based rendering of the artwork.  This will
        return a single pixel image on failure (dumb),
        but is generally a quick acid-test for whether
        the file is even possibly correct.

        It returns a np.array() of the image data for
        further analysis by the calling unit-test.
        '''
        # Stupid check #1, file exists
        self.assertTrue(os.path.exists(filepath))

        # Next, make sure it gets through gerbv export
        pngPath = self._call_gerbv_on_files([filepath])

        # gerbv made it through.  next check the output file is a valid png
        pngData = patched_imread(pngPath)

        # Sanity check the size
        self.assertTrue(pngData.shape > (1, 1))

        return pngData

    def _check_gerber_folder(self, folderPath):
        '''
        This call checks a folder full of gerber files.
        It checks each file individually, then also generates
        a binary composited image representing the superpositon
        of all of the files.  This is used to check alignments
        and multi-file registrations.
        '''
        paths = [os.path.join(folderPath, p) for p in os.listdir(folderPath)]
        for p in paths:
            self._check_gerber_file(p)

        pngPath = self._call_gerbv_on_files(paths)

        return patched_imread(pngPath)

    def _count_objects_in_img(self, img):
        from scipy.ndimage import label
        _, count = label(img)
        return count

    def _count_objects_in_file(self, filepath):
        img = self._check_gerber_file(filepath)
        return self._count_objects_in_img(img)
