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
