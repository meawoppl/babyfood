from babyfood.PCBUnits import mm, inch


class DrillWriter:
    def __init__(self, pathOrFlo):
        """
        Takes in a file-like object, or path name and initializes
        a "DrillWriter" instance for writing .xln drill files.  
        The file is opened initially, but only written when the 
        finalize() call is made.  This allows holes of the same
        diameter to be coalesced into a single tool description.
        """
        if hasattr(pathOrFlo, "write"):
            self.f = pathOrFlo
        else:
            self.f = open(pathOrFlo, "w")

        self.holes = {}
        self.formatSetup = False
        self.finalized = False

    def _fCheck(self):
        assert not self.finalized, "Already finalized"

    def _forceSetup(self):
        if not self.formatSetup:
            self.setFormat()

    def setFormat(self, fmt=(3, 3), units="METRIC"):
        assert units in ["INCH", "METRIC"]
        self._fCheck()

        self.fmt = fmt
        self.units = units
        self.uc = {"INCH": inch, "METRIC": mm}[units]

        self.formatSetup = True

    def addHole(self, xLoc, yLoc, diameter):
        """
        Add a hole at the specified x,y location with the designated diameter.
        """
        self._fCheck()
        self._forceSetup()
        diameter = self.uc(diameter)
        self.holes[diameter] = self.holes.get(diameter, []) + [(self.uc(xLoc), self.uc(yLoc))]

    def addHoles(self, xs, ys, ds):
        """
        Add holes based on three (x,y,d) interators.
        """
        self._fCheck()
        for x, y, d in zip(xs, ys, ds):
            self.addHole(x, y, d)

    def _writeHeader(self):
        self._forceSetup()
        self.f.write("M48\n")
        self.f.write(";FILE_FORMAT=%i:%i\n" % self.fmt)
        self.f.write(self.units + "\n")
        self.f.write(";TYPE=PLATED\n")

    def _getUniqueHoleSizes(self):
        uniqueHoleSizes = list(self.holes.keys())
        uniqueHoleSizes.sort()
        return uniqueHoleSizes

    def _writeTools(self):
        uniqueHoleSizes = self._getUniqueHoleSizes()

        # MRG Hack: gerbv want to see at least 1 tool even if unused
        if len(uniqueHoleSizes) == 0:
            uniqueHoleSizes = [1]

        for n, holeSize in enumerate(uniqueHoleSizes):
            tCode = "T%i" % (n + 1)
            holeSizeStr = self._fmtFloat(holeSize)
            self.f.write(tCode + "F00S00C" + holeSizeStr + "\n")
        self.f.write("%\n")

    def _fmtFloat(self, fl, decimal=True):
        b, a = self.fmt
        fmtString = "%+0" + str(b + a + 2) + "." + str(a) + "f"
        result = fmtString % fl
        result = result.replace("+", "")
        if not decimal:
            result = result.replace(".", "")
        return result

    def _writeHoles(self):
        uniqueHoleSizes = self._getUniqueHoleSizes()

        for n, holeSize in enumerate(uniqueHoleSizes):
            self.f.write("T%i\n" % (n + 1))

            for xC, yC in self.holes.get(holeSize, []):
                xStr = "X" + self._fmtFloat(xC)
                yStr = "Y" + self._fmtFloat(yC)
                self.f.write(xStr + yStr + "\n")

    def finalize(self):
        """
        Write the header, tools, holes, and finish the file.  
        """
        self._fCheck()
        self._writeHeader()
        self._writeTools()
        self._writeHoles()
        self.f.write("M30\n")
        self.f.close()
        self.finalized = True
