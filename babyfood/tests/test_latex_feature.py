import os
import random


def test_imports():
    from babyfood.features.latex import TexFeature
    TexFeature


from babyfood.features.latex import TexFeature
hexChar = lambda: random.choice("0123456789abcdef")


def makeHexCube(size=16):
    string = ""
    for x in range(size):
        for y in range(size):
            string += hexChar
        string += "\n\n"
    return string


def test_latex_text_extract():
    tf = TexFeature()

    tf.textToSVG("0123456789abcdef")
    tf.textToSVG(makeHexCube)


def test_latex_math_extract():
    tf = TexFeature()

    tf.textToSVG("$1+1$")
    tf.textToSVG("$\int_0^1 1dx$")
    tf.textToSVG("$1+\infty$")


def test_latex_math_replay():
    tf = TexFeature()

    tf.textToSVG("$1+1$")
    tf.textToSVG("$\int_0^1 1dx$")
    tf.textToSVG("$1+\infty$")

from babyfood.tests.shared import GerbvTester, _quickTempFilePath


class LatexGerberTester(GerbvTester):
    def _latex_helper(self, text):
        from babyfood.pcb.OSHParkPCB import OSHParkPCB
        outputFolderName = _quickTempFilePath()
        if not os.path.exists(outputFolderName):
            os.makedirs(outputFolderName)
        pcb = OSHParkPCB(outputFolderName)

        pcb.setActiveSide("top")
        pcb.setActiveLayer("overlay")

        tf1 = TexFeature()
        tf1.setText(text, pcb, fill=True)

        pcb.finalize()

        # Return a path to the active gerber for testing
        return pcb.getCurrentLayerFilePath()

    def test_latex_simple(self):
        tex = r"""\LaTeX"""
        gerberPath = self._latex_helper(tex)
        self.assertEqual(self._count_objects_in_file(gerberPath), 3)

    def test_latex_harder(self):
        tex = r"""$1+2+3+4$"""
        gerberPath = self._latex_helper(tex)
        self.assertEqual(self._count_objects_in_file(gerberPath), 7)

    def test_latex_hard(self):
        tex = r"""$1+2+3+4$


                  $\oint$"""
        gerberPath = self._latex_helper(tex)
        self.assertEqual(self._count_objects_in_file(gerberPath), 8)

    def test_latex_brutal(self, text=None):

        demoTex = r"""Kerning: fj AW Awa Ta

                      Ligatures: fj ffi fl tt

                      Math: $\int_0^{\infty}x \mathrm{d}x$
                      """
        gerberPath = self._latex_helper(demoTex)
        self.assertEqual(self._count_objects_in_file(gerberPath), 51)

