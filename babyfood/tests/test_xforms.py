import unittest

import numpy as np

from babyfood.homogenous import HomogenousTransform

class XFormTestCase(unittest.TestCase):
	def assertClose(self, v1, v2):
		close = np.allclose(v1, v2)
		if not close:
			print("Deltas", v1 - v2)
		self.assertTrue(close)

	def test_xform_init(self):
		# Two ways to make identity transforms
		ht1 = HomogenousTransform()
		ht2 = HomogenousTransform(np.eye(3))

		inShape = (2, 13)
		in1 = np.ones(inShape)

		out1 = ht1.project(in1)
		out2 = ht2.project(in1)

		self.assertTrue(out1.shape == inShape )
		self.assertTrue(out2.shape == inShape )
		self.assertTrue(np.all(in1 == out1))
		self.assertTrue(np.all(in1 == out1))


	def test_xform_shape(self):
		ht = HomogenousTransform()

		inShape = (2, 13)
		in1 = np.ones(inShape)
		out1 = ht.project(in1)

		self.assertTrue(in1.shape == out1.shape)


	def test_translation(self):
		ht = HomogenousTransform.translation(5, 5)
		inp = np.zeros((2, 10))
		otp = ht.project(inp)

		self.assertClose(otp, 5)

	def test_scale_unity(self):
		ht = HomogenousTransform.scaling(1, 1)
		inp = np.ones((2, 10))
		otp = ht.project(inp)

		self.assertClose(inp, otp)

	def test_scale_double(self):
		ht = HomogenousTransform.scaling(2, 2)
		inp = np.ones((2, 10))
		otp = ht.project(inp)

		self.assertClose(otp, 2)

	def test_xfrom_product(self):
		# 1 full rotation in four steps
		ht = HomogenousTransform.rotation(np.pi / 2)
		unityTransform = ht * ht * ht * ht

		inp = np.ones((2, 10))
		otp = unityTransform.project(inp)

		self.assertClose(otp, inp)
