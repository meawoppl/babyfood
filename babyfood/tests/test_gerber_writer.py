import os, random, subprocess, tempfile, unittest

from scipy import misc

from babyfood.io.GerberWriter import GerberWriter

# Just see if gerbv is alive and kicking
_gerbvTestCall = ("gerbv", "-V")

# Call with 100dpi, and no border
_gerbvCalibratedCall = ("gerbv", "-D 512x512", "-B 0")

# MRG NB: fast, but not secure, hacky, bad. XXX
def _quickTempFilePath(suffix):
	characters = ("abcdefghijklmnopqrstuvwxyz" +
		          "ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
                  "0123456789_")
	name = "".join([random.choice(characters) for c in range(10)]) + suffix
	path = os.path.join(tempfile.gettempdir(), name)
	return path

class GerberWriterTestCase(unittest.TestCase):
	def test_gerbv_exists(self):
		result = subprocess.check_call(_gerbvTestCall)
		self.assertEqual(result, 0)

	def test_gerbv_version(self):
		output = subprocess.check_output(_gerbvTestCall).decode("UTF-8")
		versionString = output.split()[2]
		versionTuple = tuple([int(vn) for vn in versionString.split(".")])
		newEnough = versionTuple > (2, 5, 0)
		if not newEnough:
			print("Gerbv version:" + versionTuple)
		self.assertTrue(newEnough)
	
	def _check_gerber_file(self, filepath):
		# Stupid check #1
		self.assertTrue(os.path.exists(filepath))

		# Next, make sure it get through gerbv export
		pngPath = _quickTempFilePath(".png")
		gvCall = _gerbvCalibratedCall + ("-x", "png", "-o", pngPath)
		callSuccess = subprocess.check_call(gvCall) == 0
		self.assertTrue(callSuccess)

		self.assertTrue(os.path.exists(pngPath))

		# Nice.  gerbv made it through.  next check the output file is a valid png
		pngData = misc.imread(pngPath, flatten=True)
		return pngData

	def test_gw_line(self):
		gerbFilePath = _quickTempFilePath(".gbr")
		gw = GerberWriter(gerbFilePath)

		gw.defineCircularAperature(0.25, True)
		gw.moveTo(1, 1)
		gw.lineTo(-1, -1)
		gw.finalize()

		d = self._check_gerber_file(gerbFilePath)
		print(d)
