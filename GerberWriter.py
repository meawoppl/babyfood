import time
from warnings import warn

import numpy as np

from PCBUnits import mm, inch


def pointsClose(pt1, pt2, eps=1e-8):
    x1, y1 = pt1
    x2, y2 = pt2

    dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist < eps


def iteratePairs(iterable):
    last = None
    for idx in range(len(iterable) - 1):
        nxt = iterable.next()
        if last is not None:
            yield last, nxt
        last = nxt


def formatFloat(fl, fmt=(4, 4)):
    stringFmt = "%.0" + str(fmt[1]) + "f"
    string = stringFmt % fl
    intPos, decPos = string.split(".")

    if len(intPos) > fmt[0]:
        warn("WARNING: position %f is getting truncated (msb)!")
        intPos = intPos[0:3]

    return intPos + decPos


def fmtCoord(xLoc, yLoc, xFmt=(4, 4), yFmt=(4, 4), xLab="X", yLab="Y"):
    return xLab + formatFloat(xLoc, fmt=xFmt) + yLab + formatFloat(yLoc, fmt=yFmt)


class GerberWriter:
    def __init__(self, pathOrFlo):
        if hasattr(pathOrFlo, "write"):
            self.f = pathOrFlo
        else:
            self.f = open(pathOrFlo, "w")

        # Flags to track the current file state
        self.headerWritten = False
        self.formatSet = False
        self.polaritySet = False
        self.aprDict = {}

        self.currentX = 0
        self.currentY = 0

    def setCoordFmt(self, xFmt=(4, 4), yFmt=(4, 4), units="MM"):
        assert units in ["MM", "IN"], "Units much be IN or MM"
        assert len(xFmt) == 2
        assert len(yFmt) == 2
        # MRG TODO: max extents and bounds of coord?
        self.xFmt = xFmt
        self.yFmt = yFmt

        # Unit converdsion function
        self.uc = {"MM": mm, "IN": inch}[units]

        self.units = units
        self.formatSet = True

    def writeComment(self, comment):
        assert "*" not in comment, "* character not allowed in comments"
        self.f.write("G04" + comment + "*\n")

    def writeGerberHeader(self, comment=None):
        if comment is None:
            comment = "Autogenerated by babyfood by MRG." + time.ctime()
        self.writeComment(comment)

        # If the coordinate format hs not been set yet, put in the defaults
        if not self.formatSet:
            self.setCoordFmt()

        fmtStr = "X%i%iY%i%i" % (self.xFmt + self.yFmt)
        self.f.write("%FSLA" + fmtStr + "*%\n")
        self.f.write("%MO" + self.units + "*%\n")

        self.headerWritten = True

    def writeLayerPolarity(self, polarity="D"):
        self._forceHeader()
        assert polarity in ["D", "C"]
        self.f.write("%LP" + polarity + "*%\n")
        self.polaritySet = True

    def _forceHeader(self):
        if not self.headerWritten:
            self.writeGerberHeader()

    def _forcePolarity(self):
        if not self.polaritySet:
            self.writeLayerPolarity()

    def _checkAperature(self):
        if not self.currentAperatureCode:
            raise RuntimeError("No Aperature defined for current move!")

    def _preGraphicsCheck(self):
        self._forceHeader()
        self._forcePolarity()

    def defineCircularAperature(self, diameter, setAsCurrent=False):
        aprDescriptor = "C,%0.03f" % diameter
        aprCode = self._defineAperature(aprDescriptor, setAsCurrent)
        return aprCode

    def _defineAperature(self, aprString, setAsCurrent):
        self._preGraphicsCheck()
        
        if aprString not in self.aprDict:
            newAprCode = "D%i" % (10 + len(self.aprDict))
            self.f.write("%AD" + newAprCode + aprString + "*%\n")
            self.aprDict[aprString] = newAprCode 
        
        if len(self.aprDict) > 999:
            warn("WARNING! Aperature counts above 999 not supported by all machines.")

        thisAprCode = self.aprDict[aprString]

        if setAsCurrent:
            self.setAperature(thisAprCode)

        return thisAprCode

    def setAperature(self, aprCode):
        assert aprCode in self.aprDict.values(), aprCode + " is not in " + str(self.aprDict)
        self.f.write(aprCode + "*\n")

    def finalize(self):
        self.f.write("M02*\n")
        self.f.close()

    def _linearMove(self, endX, endY, dCode):
        '''Low level command which encompasses all linear moves,
        This includes light, dark, and flash moves'''
        self._preGraphicsCheck()

        # unit sanitize
        endX = float(self.uc(endX))
        endY = float(self.uc(endY))

        formattedCoords = fmtCoord(endX, endY, self.xFmt, self.yFmt)
        dCodeStr = "D%02i" % dCode
        # Stroke w/ current aperature
        if dCode == 1:
            cmdString = "G01" + formattedCoords + dCodeStr
        # Light off move and flash
        elif dCode in [2, 3]:
            cmdString = formattedCoords + dCodeStr
        else:
            raise RuntimeError("Unrecognized dCode " + dCodeStr)
        self.f.write(cmdString + "*\n")

        self.currentX = endX
        self.currentY = endY

    def moveTo(self, newX, newY):
        self._linearMove(newX, newY, 2)

    def lineTo(self, newX, newY):
        self._linearMove(newX, newY, 1)

    def flashAt(self, newX, newY):
        self._linearMove(newX, newY, 3)

    def _arcMove(self, endX, endY, cX, cY, direction, dCode=1):
        self._preGraphicsCheck()

        # Unit flatten to the file unit types
        endX = float(self.uc(endX))
        endY = float(self.uc(endY))
        cX = float(self.uc(cX))
        cY = float(self.uc(cY))

        # Make estiamates of the radius, and sanity check the coords
        rEst1 = np.sqrt((self.currentX - cX) ** 2 + (self.currentY - cY) ** 2)
        rEst2 = np.sqrt((endX - cX) ** 2 + (endY - cY) ** 2)
        if np.abs(rEst1 - rEst2) > 0.001:
            warn("WARNING: Large deviation in computed radius in arc-move!")

        dCode = "D%02i" % dCode

        if direction == "CW":
            gCode = "G02"
        elif direction == "CCW":
            gCode = "G03"
        else:
            raise RuntimeError("Direction must be CW or CCW!")

        # Compute the offset of the circle center point from the starting coordiante
        xOffset = cX - self.currentX
        yOffset = cY - self.currentY

        # Assemble the command string
        cmdString = gCode
        cmdString += fmtCoord(endX, endY)
        cmdString += fmtCoord(xOffset, yOffset, xLab="I", yLab="J")
        cmdString += dCode

        # Set to multi-quadrant mode
        self.f.write("G75*\n")

        # Write it
        self.f.write(cmdString + "*\n")

        # Update the internal position tracker
        self.currentX = endX
        self.currentY = endY

    def arcLineTo(self, endX, endY, cX, cY, direction):
        self._arcMove(endX, endY, cX, cY, direction)

    def circle(self, cx, cy, cr):
        self.moveTo(cx - cr, cy)
        self.arcLineTo(cx - cr, cy, cx, cy, "CW")

    def simplePolygon(self, xs, ys):
        # Start "polygon mode"
        self.f.write("G36*\n")
        for n, (xC, yC) in enumerate(zip(xs, ys)):
            if n == 0:
                # Move to the start point
                self._linearMove(xC, yC, 2)
            else:
                # Trace the next segment
                self._linearMove(xC, yC, 1)
        # If the start and end points are not equal, close the loop
        if not pointsClose((xs[0], ys[0]), (xs[-1], ys[-1])):
            self._linearMove(xs[0], ys[0], 1)
            warn("WARNING: Call to polygon is getting automatically closed!")
        # Finish the contour
        self.f.write("G37*\n")

    def filledCircle(self, x, y, r):
        self.f.write("G36*\n")
        self.circle(x, y, r)
        # Finish the contour
        self.f.write("G37*\n")

if __name__ == "__main__":
    # Quick test of building functionality
    gw = GerberWriter("gwTest.gbo")
    gw.defineAperature(0.25, True)
    gw.move(0, 0)
    gw.lineTo(10, 0)
    gw.lineTo(10, 10)
    gw.lineTo(0, 10)
    gw.lineTo(0, 0)

    gw.flashAt(4, 2)
    gw.flashAt(2, 2)
    gw.flashAt(2, 4)
    gw.flashAt(4, 4)

    for n, r in enumerate(np.linspace(0, 5, 11)[::-1]):
        t = np.linspace(0, 2 * np.pi, 7) + r * 0.3
        xs = r * np.cos(t) + 5
        ys = r * np.sin(t) + 5
        gw.writeLayerPolarity(["D", "C"][n % 2])
        gw.simplePolygon(xs, ys)

    gw.finalize()
