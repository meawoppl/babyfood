
class DrillWriter:
    def __init__(self, pathOrFlo):
        if hasattr(pathOrFlo, "write"):
            self.f = pathOrFlo
        else:
            self.f = open(pathOrFlo, "w")

        print("DW Init", pathOrFlo)
        self.holes = {}
        self.formatSetup = False

    def setFormat(self, fmt=(3, 3), units="METRIC"):
        assert units in ["INCH", "METRIC"]
        self.fmt = fmt
        self.units = units
        self.formatSetup = True

    def _forceSetup(self):
        if not self.formatSetup:
            self.setFormat()

    def addHole(self, xLoc, yLoc, diameter):
        self._forceSetup()
        print("Adding hole:", xLoc, yLoc, diameter)
        self.holes[diameter] = self.holes.get(diameter, []) + [(xLoc, yLoc)]

    def addHoles(self, xs, ys, ds):
        for x, y, d in zip(xs, ys, ds):
            self.addHole(x, y, d)

    def writeHeader(self):
        self._forceSetup()
        self.f.write("M48\n")
        self.f.write(";FILE_FORMAT=%i:%i\n" % self.fmt)
        self.f.write(self.units + "\n")
        self.f.write(";TYPE=PLATED\n")
        self.writeTools()
        self.f.write("%\n")

    def _getUniqueHoleSizes(self):
        uniqueHoleSizes = list(self.holes.keys())
        uniqueHoleSizes.sort()
        return uniqueHoleSizes

    def writeTools(self):
        uniqueHoleSizes = self._getUniqueHoleSizes()

        # MRG Hack: gerbv want to see at least 1 tool even if unused
        if len(uniqueHoleSizes) == 0:
            uniqueHoleSizes = [1]

        for n, holeSize in enumerate(uniqueHoleSizes):
            tCode = "T%i" % (n + 1)
            holeSizeStr = self._fmtFloat(holeSize)
            self.f.write(tCode + "F00S00C" + holeSizeStr + "\n")

    def _fmtFloat(self, fl, decimal=True):
        b, a = self.fmt
        fmtString = "%+0" + str(b + a + 2) + "." + str(a) + "f"
        result = fmtString % fl
        result = result.replace("+", "")
        if not decimal:
            result = result.replace(".", "")
        return result

    def writeHoles(self):
        uniqueHoleSizes = self._getUniqueHoleSizes()

        for n, holeSize in enumerate(uniqueHoleSizes):
            self.f.write("T%i\n" % (n + 1))

            for xC, yC in self.holes.get(holeSize, []):
                xStr = "X" + self._fmtFloat(xC)
                yStr = "Y" + self._fmtFloat(yC)
                self.f.write(xStr + yStr + "\n")

    def finalize(self):
        self.writeHeader()
        self.writeHoles()
        self.f.write("M30\n")
        self.f.close()


if __name__ == "__main__":
    dw = DrillWriter("dwTest.drl")
    dw.addHole(1, 1, 0.1)
    dw.finalize()
