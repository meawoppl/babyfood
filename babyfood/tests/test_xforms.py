import unittest, random

import numpy as np

from babyfood.homogenous import HomogenousTransform, TransformationContext

class ABCHelpers(unittest.TestCase):
    def assertClose(self, v1, v2):
        close = np.allclose(v1, v2)
        if not close:
            print("Deltas:")
            print(v1 - v2)
        self.assertTrue(close)

class BaseXFormTestCase(ABCHelpers):
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
        ht = HomogenousTransform.scaling(1)
        inp = np.ones((2, 10))
        otp = ht.project(inp)

        self.assertClose(inp, otp)

    def test_scale_double(self):
        ht = HomogenousTransform.scaling(2)
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


class ContextedXFormTestCase(ABCHelpers):
    def test_xform_ctx(self):
        tc = TransformationContext()

        # origin identity
        inp = np.zeros((2, 10))
        out = tc.project(inp)
        self.assertClose(inp, out)

        # Unit identity
        inp = np.ones((2, 10))
        out = tc.project(inp)
        self.assertClose(inp, out)

    def test_xform_ctx_identity(self):
        tc = TransformationContext()

        # Rotation should not affect the origin
        inp = np.zeros((2, 10))
        with tc.rotation(10):
            r = tc.project(inp)
        self.assertClose(r, np.zeros((2,10)))


    def test_xform_ctx_rotation_identity(self):
        tc = TransformationContext()

        # Rotation should not affect the origin
        inp = np.zeros((2, 10))
        with tc.rotation(10):
            r = tc.project(inp)
        self.assertClose(r, np.zeros((2,10)))

    def test_xform_ctx_rotation(self):
        tc = TransformationContext()

        inp = np.zeros((2, 10))
        inp[0, :] = 1
        with tc.rotation(np.pi/4):
            r = tc.project(inp)

        self.assertClose(r, np.sqrt(2)/2)

    def test_xform_ctx_rotation_multi(self):
        tc = TransformationContext()

        inp = np.zeros((2, 10))
        inp[0, :] = 1
        with tc.rotation(np.pi/8):
            with tc.rotation(np.pi/8):
                r = tc.project(inp)

        self.assertClose(r, np.sqrt(2)/2)

    def test_xform_ctx_multi(self):
        tc = TransformationContext()

        inp = np.zeros((2, 10))
        with tc.rotation(np.pi/4):
            with tc.translation(1, 0):
                r = tc.project(inp)

        self.assertClose(r, np.sqrt(2)/2)


    def test_xform_ctx_hard(self):
        tc = TransformationContext()

        inp = np.zeros((2, 10))
        inp[0, :] = 1

        # Big stack of unit rotations . . .
        # that work out unitary:)
        with tc.rotation(2 * np.pi * 25):
            with tc.rotation(2 * np.pi * 25):
                with tc.rotation(2 * np.pi * 25):
                    with tc.rotation(2 * np.pi * 25):
                        r = tc.project(inp)

        self.assertClose(inp, r)

    def test_xform_ctx_unwind(self):
        tc = TransformationContext()

        inp = np.zeros((2, 10))
        inp[0, :] = 1

        with tc.rotation(np.pi / 4):
            with tc.rotation(np.random.uniform(0, 2*np.pi)):
                with tc.rotation(np.random.uniform(0, 2*np.pi)):
                    cruft = tc.project(inp)
            # Check that the nested context is restored 
            r = tc.project(inp)

        self.assertClose(r, np.sqrt(2) / 2)
