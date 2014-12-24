from freetype import Face

import numpy as np
from pylab import axis, close, figure, plot, show


def unpackCharacter(glyph):
    outline = glyph.outline
    points = np.array(outline.points, dtype=float)

    # Find the start and stop points for each loop in the segment list
    starts = [0] + [s + 1 for s in outline.contours[:-1]]
    ends = list(outline.contours)

    loopSets = []
    # Iterate over the loops
    for start, end in zip(starts, ends):
        points = outline.points[start: end + 1]
        tags = outline.tags[start:end + 1]

        points.append(points[0])
        tags.append(tags[0])

        segments = [[]]
        for n, (pt, tg) in enumerate(zip(points, tags)):
            segments[-1].append(pt)
            if n == 0:
                continue
            newSegmentFlag = (tg & 1)
            notTheEndPoint = n < (len(points) - 1)
            if newSegmentFlag and notTheEndPoint:
                segments.append([pt, ])

        mySegmentList = []
        for segment in segments:
            if len(segment) in [2, 3]:
                mySegmentList.append(segment)
            else:
                mySegmentList.extend(breakPackedSplineIntoBezier(segment))
        loopSets.append(mySegmentList)

    return loopSets


def breakPackedSplineIntoBezier(segmentData):
    returnSegments = []
    for i in range(len(segmentData)):
        a, c, e = segmentData[i:i + 3]
        b = ((a[0] + c[0]) / 2.0, (a[1] + c[1]) / 2.0)
        d = ((c[0] + e[0]) / 2.0, (c[1] + e[1]) / 2.0)
        # First segment
        if i == 0:
            returnSegments.append((a, c, d))
            continue
        # Last Segment
        if i == len(segmentData) - 3:
            returnSegments.append((b, c, e))
            break
        # All the middle segments
        returnSegments.append((b, c, d))
    return returnSegments


def computeQuadBezier(pt1, pt2, pt3, nPoints=4):
    t = np.linspace(0, 1, nPoints)
    xs = ((1 - t) ** 2 * pt1[0]) + (2 * (1 - t) * t * pt2[0]) + (t ** 2 * pt3[0])
    ys = ((1 - t) ** 2 * pt1[1]) + (2 * (1 - t) * t * pt2[1]) + (t ** 2 * pt3[1])
    return xs, ys


def plotQuadBezier(pt1, pt2, pt3, nPoints=10):
    xs, ys = computeQuadBezier(pt1, pt2, pt3, nPoints)
    plot(xs, ys, "g", linewidth=5, alpha=0.3)


def plotLoopSets(loopSets):
    for loop in loopSets:
        for seg in loop:
            if len(seg) == 2:
                plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]], 'b', linewidth=5, alpha=0.3)
            if len(seg) == 3:
                A, B, C = seg
                plot([A[0], B[0], C[0]], [A[1], B[1], C[1]], 'r:', linewidth=2)
                plotQuadBezier(*tuple(seg))


def loopToPolygon(loop, bezN=10):
    pts = []
    for segment in loop:
        if len(segment) == 2:
            pts.extend(segment)
        if len(segment) == 3:
            [pts.append(x, y) for x, y in computeQuadBezier(*tuple(segment), nPoints=bezN)]
    assert pts[0] == pts[-1]
    return pts


def loopsToPolygons(loopSets):
    return [loopToPolygon(loop) for loop in loopSets]


def shiftLoopSet(loopSets, xS, yS):
    newLoopSet = []
    for loop in loopSets:
        newLoop = []
        for seg in loop:
            newSeg = [(x + xS, y + yS) for x, y in seg]
            newLoop.append(newSeg)
        newLoopSet.append(newLoop)
    return newLoopSet


def plotTextString(stringToPlot, kerning=False, startXY=(0,0)):
    fontPath = "/home/meawoppl/Dropbox/repos/babyfood/cmr10.pfb"
    typeFace = Face(fontPath)
    typeFace.attach_file("/home/meawoppl/Dropbox/repos/babyfood/cmr10.pfm")
    typeFace.set_char_size(48 * 64)

    figure()
    startX, startY = startXY
    for n, char in enumerate(stringToPlot):
        typeFace.load_char(char)
        loopz = unpackCharacter(typeFace.glyph)
        loopz = shiftLoopSet(loopz, startX, startY)
        startX += typeFace.glyph.advance.x
        startY += typeFace.glyph.advance.y
        if kerning and (n != 0):
            kv = typeFace.get_kerning(char, stringToPlot[n-1])
            print(char, stringToPlot[n-1])
            print(kv.x, kv.y)
            print(dir(kv))
            startX += kv.x

        plotLoopSets(loopz)
    axis("equal")
    show()
    close()


class TextFeature(SingleLayerFeature):
    def __init__(self, layerName, text):
        SingleLayerFeature.__init__(self, layerName)
        self.text = text
    def artist(self, gerberWriter):
        
        gerberWriter


if __name__ == "__main__":
    plotTextString("The quick brown fox jumped over the lazy dogs.", kerning = True)
