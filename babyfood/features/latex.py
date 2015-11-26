import os
import subprocess
import tempfile
from pprint import pprint

import numpy as np
from bs4 import BeautifulSoup

texTemplate = '''\\documentclass{article}
%s
\\begin{document}
\\thispagestyle{empty}
%s
\\end{document}"
'''

from pylab import plot, show, title


class PathParsePlay:
    def __init__(self, pathString):
        self._parsePathString(pathString)

        self.commandFuncs = {"M": self._play_M,
                             "L": self._play_L,
                             "C": self._play_C,
                             "Z": self._play_Z}

    def _parsePathString(self, pathString):
        # Parse a xvg "path" element:
        # http://www.w3.org/TR/SVG/paths.html#PathDataGeneralInformation

        # Break it into strings
        pathElements = pathString.split()

        # Break this into a list of commands and linked numbers
        self.commandList = []
        currentCommand = []
        for element in pathElements:
            try:
                currentCommand.append(float(element))
            except ValueError:
                if currentCommand != []:
                    self.commandList.append(currentCommand)
                currentCommand = [element]

        # Break the command list into paths and subpaths
        pathSegments = [[]]
        for n, command in enumerate(self.commandList):
            pathSegments[-1].append(command)

            isSegmentEnd = command[0].lower() == "z"
            if isSegmentEnd:
                pathSegments.append([])

        # Screen out empty segments.  These appear in SVG's often
        # This also allows the above logic to be a bit sloppy
        pathSegments = [seg for seg in pathSegments if seg != []]

        # Compute the handedness of each segment, and
        # bucket in into solids and holes
        signs = [self._calculate_path_handedness(seg) for seg in pathSegments]
        self.solids = []
        self.holes = []
        for sign, segment in zip(signs, pathSegments):
            if sign == 1:
                self.solids.append(segment)
            if sign == -1:
                self.holes.append(segment)

    def _calculate_path_handedness(self, path):
        assert path[0][0].lower() == "m"
        assert path[-1][0].lower() == "z"

        startX, startY = path[0][-2:]
        x1, y1 = startX, startY

        edgeSum = 0
        for cmd in path[1:]:
            if cmd[0].lower() == "z":
                x2, y2 = startX, startY
            else:
                x2, y2 = cmd[-2:]

            edgeSum += (x2 - x1) * (y2 + y1)

            # plot([x1, x2], [y1, y2], "b", linewidth=4)
            x1, y1 = x2, y2

        # title(str(edgeSum))
        # show()

        sign = int(edgeSum / abs(edgeSum))
        assert sign in [-1, 1]
        return sign

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

    def _playCommandList(self, ctx, cmdList):
        self.startPos = None

        for command in cmdList:
            moveName, *numbers = command
            self.commandFuncs[moveName](ctx, numbers)

    def playOutlineIntoContext(self, ctx):
        ctx.setLayerPolarity("D")
        for segment in self.solids:
            self._playCommandList(ctx, segment)

        for segment in self.holes:
            self._playCommandList(ctx, segment)

    def playFilledIntoContext(self, ctx):
        ctx.setLayerPolarity("D")
        for segment in self.solids:
            with ctx.polygonMode():
                self._playCommandList(ctx, segment)

        ctx.setLayerPolarity("C")
        for segment in self.holes:
            with ctx.polygonMode():
                self._playCommandList(ctx, segment)

        ctx.setLayerPolarity("D")


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
        call = ("pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                "-output-directory", d, texFile.name)
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
        svgData = open(svgPath, "rb").read()
        # MRG NOTE: If "rb" is not specified above, beautiful soup appeaars
        # To produce _unstable_ output.  This seems like a library bug probably
        # from poor py2 -> py3 portage?
        return BeautifulSoup(svgData, "lxml")

    def setText(self, textToRender, ctx, fill=True):
        svgSoup = self.textToSVG(textToRender)

        # Extract all the "glyphs"
        # This is roughly 1/symbol
        defsG = svgSoup.svg.defs.g
        glyphNameToPathPlayer = {}
        allPaths = defsG.find_all("symbol")
        for symbol in allPaths:
            # Extract the pathing string
            pathString = symbol.path["d"]
            # Parse the string, and store it keyed to the glyph name
            ppp = PathParsePlay(pathString)
            glyphNameToPathPlayer[symbol["id"]] = ppp

        # Find the strikes of the above symbols
        for gee in svgSoup.svg.find_all("g", recursive=False):
            for use in gee.find_all("use"):
                # Dereference the ID to the glyph to draw
                strikeID = use["xlink:href"][1:]
                ppp = glyphNameToPathPlayer[strikeID]

                # Determine where the symbol goes, and
                # scooch the context to there
                x, y = float(use["x"]), float(use["y"])
                with ctx.transform.flipY():
                    with ctx.transform.translation(x, y):
                        # Draw the symbol!
                        if fill:
                            ppp.playFilledIntoContext(ctx)
                        else:
                            ppp.playOutlineIntoContext(ctx)

if __name__ == "__main__":
    demoTex = r"""Kerning: fj AW Awa Ta

                  Ligatures: fj ffi fl tt

                  Math: $\int_0^{\infty}x \mathrm{d}x$
                  """

    # demoTex = r"""ABC

    #             ASD

    #             $1+1$
    # """
    # demoTex = r"""Math: $\int_0^{\infty}{x \mathrm{d}x}$""" + "\n\n"
    # demoTex = demoTex * 2

    from babyfood.pcb.OSHParkPCB import OSHParkPCB
    outputFolderName = "/home/meawoppl/bf/textest"
    if not os.path.exists(outputFolderName):
        os.makedirs(outputFolderName)
    pcb = OSHParkPCB(outputFolderName)

    pcb.setActiveSide("top")
    pcb.setActiveLayer("overlay")

    tf1 = TexFeature()
    tf1.setText(demoTex, pcb, fill=True)

    print("Filled:")
    tf2 = TexFeature()
    with pcb.transform.translation(0, -50):
        tf2.setText(demoTex, pcb, fill=False)

    tf3 = TexFeature()
    with pcb.transform.translation(0, -100):
        tf3.setText(demoTex, pcb, fill=False)

    pcb.finalize()
    pcb.visualize()
