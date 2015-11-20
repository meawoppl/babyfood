import os
import subprocess
import tempfile

import numpy as np
from bs4 import BeautifulSoup

texTemplate = '''\\documentclass{article}
%s
\\begin{document}
\\thispagestyle{empty}
%s
\\end{document}"
'''


class PathParsePlay:
    def __init__(self, pathString):
        self.parsePathString(pathString)

        self.commandFuncs = {"M": self._play_M,
                             "L": self._play_L,
                             "C": self._play_C,
                             "Z": self._play_Z}
        self.startPos = None

    def parsePathString(self, pathString):
        # MRG TODO: Document me
        pathElements = pathString.split()

        self.commandList = []
        currentCommand = []
        for element in pathElements:
            try:
                currentCommand.append(float(element))
            except ValueError:
                if currentCommand != []:
                    self.commandList.append(currentCommand)
                currentCommand = [element]

    def _play_M(self, ctx, numbers):
        numbers = np.array(numbers).reshape((-1, 2))
        startX, startY = numbers[0, :]
        ctx.moveTo(startX, startY)

        if self.startPos is None:
            self.startPos = startX, startY

        self._currentXY = startX, startY

        # Additional points become line segments
        self._play_L(ctx, numbers[1:, :])

    def _play_L(self, ctx, numbers):
        numbers = np.array(numbers).reshape((-1, 2))

        for x, y in numbers:
            ctx.lineTo(x, y)
            self._currentXY = x, y

    def _play_C(self, ctx, numbers, nSteps=10):
        x1, y1 = self._currentXY
        x2, y2, x3, y3, x4, y4 = tuple(numbers)

        for i in range(1, nSteps + 1):
            t = i / nSteps

            omt = 1 - t

            xt = ((omt ** 3 * x1 * 1 * t ** 0) +
                  (omt ** 2 * x2 * 3 * t ** 1) +
                  (omt ** 1 * x3 * 3 * t ** 2) +
                  (omt ** 0 * x4 * 1 * t ** 3))

            yt = ((omt ** 3 * y1 * 1 * t ** 0) +
                  (omt ** 2 * y2 * 3 * t ** 1) +
                  (omt ** 1 * y3 * 3 * t ** 2) +
                  (omt ** 0 * y4 * 1 * t ** 3))

            ctx.lineTo(xt, yt)

        self._currentXY = xt, yt

    def _play_Z(self, ctx, numbers):
        assert len(numbers) == 0
        ctx.lineTo(*self.startPos)
        self.startPos = None

    def playCommandListIntoContext(self, ctx):
        for command in self.commandList:
            # print(command)
            moveName, *numbers = command
            self.commandFuncs[moveName](ctx, numbers)


def quiet_check_call(call):
    import tempfile
    dn = open(os.devnull, "wb")
    dn = tempfile.TemporaryFile("w+")
    result = subprocess.check_call(call, stdout=dn, stderr=dn)
    dn.flush()
    dn.seek(0)

    return result, dn.read()


class TexFeature:
    def __init__(self, headers=""):
        self.headers = headers

    def textToSVG(self, text):
        # Create the TeX file
        d = tempfile.mkdtemp()
        texFile = tempfile.NamedTemporaryFile(mode='w+', suffix=".tex", dir=d)
        texFile.write(texTemplate % (self.headers, text))
        texFile.flush()

        # TeX -> pdf file
        call = ("pdflatex", "-output-directory", d, texFile.name)
        result, debugText = quiet_check_call(call)
        if result != 0:
            # MRG NOTE: I am not sure how too reproduce the non-zero return codes here.
            print("Possible error in latex: %i" % result)
            print("Input:")
            print("***" * 10)
            texFile.seek(0)
            print(texFile.read())
            print("***" * 10)

            print("Output:")
            print("***" * 10)
            print(debugText)
            print("***" * 10)

        # Pop a suffix off, and add a new one
        reSuffix = lambda filepath, newSuffix: os.path.splitext(filepath)[0] + "." + newSuffix

        # pdf file -> svg file
        texPath = os.path.join(d, texFile.name)
        pdfPath = reSuffix(texPath, "pdf")
        svgPath = reSuffix(texPath, "svg")

        call = ("pdf2svg", pdfPath, svgPath)
        assert quiet_check_call(call), "Error during pdf->svg conversion"

        # Read the file, and return the soup.
        svgData = open(svgPath).read()
        return BeautifulSoup(svgData, "lxml")

    def setText(self, textToRender, ctx):
        svgSoup = self.textToSVG(textToRender)

        # Extract all the "glyphs"
        defsG = svgSoup.svg.defs.g
        glyphNameToPathPlayer = {}
        allPaths = defsG.find_all("symbol")
        for n, symbol in enumerate(allPaths):
            print("=== %i (%s) ===" % (n, symbol["id"]))
            path = symbol.path
            pathString = path["d"]
            ppp = PathParsePlay(pathString)
            glyphNameToPathPlayer[symbol["id"]] = ppp
            # ppp.playCommandListIntoContext(ctx)

        # Find the strikes of the above symbols
        for gee in svgSoup.svg.find_all("g", recursive=False):
            for use in gee.find_all("use"):
                # Dereference the ID to the symbol to draw
                strikeID = use["xlink:href"][1:]
                ppp = glyphNameToPathPlayer[strikeID]

                # Determine where the symbol goes, and scooch the context
                x, y = float(use["x"]), float(use["y"])
                with ctx.transform.translation(x, y):
                    # Draw the symbol!
                    ppp.playCommandListIntoContext(ctx)


if __name__ == "__main__":
    from babyfood.pcb.OSHParkPCB import OSHParkPCB
    outputFolderName = "/home/meawoppl/bf/textest"
    if not os.path.exists(outputFolderName):
        os.makedirs(outputFolderName)
    pcb = OSHParkPCB(outputFolderName)

    pcb.setActiveSide("top")
    pcb.setActiveLayer("overlay")

    tf = TexFeature()
    with pcb.transform.flipY():
        tf.setText(r"""Ligatures: fj ffi fl

                       $\int_0^{\infty}{x \mathrm{d}x}$""", pcb)

    pcb.finalize()
    pcb.visualize()
