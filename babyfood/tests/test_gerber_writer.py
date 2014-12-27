import subprocess, unittest

_gerbvTestCall = ("gerbv", "-V")

class GerberWriterTestCase:
	def test_gerbv_exists(self):
		result = subprocess.check_call(_gerbvTestCall)
		self.assertEqual(result, 0)

	def test_gerbv_version(self, filePath):
		output = subprocess.check_output(_gerbvTestCall)
		versionString = output.split()[2]
		print("Gerbv version", versionString)
		versionTuple = versionString.split(".")
		self.assertTrue(versionTuple > (2, 0))
	