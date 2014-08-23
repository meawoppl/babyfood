from freetype import Face

import itertools
import numpy as np
from pylab import axis, close, figure, plot, show


def unpackCharacter(glyph):
    outline = glyph.outline
    points = np.array(outline.points, dtype=[('x', float), ('y', float)])
    x, y = points['x'], points['y']

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


def findClosestPair(ptList1, ptList2):
    closest = np.inf
    for pt1, pt2 in itertools.product(ptList1, ptList2):
        sub = pt1 - pt2
        dist = np.linalg.norm(sub, sub)
        if dist < closest:
            closest = dist
            i1, i2 = pt1, pt2
    return i1, i2


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


def computeQuadBezier(pt1, pt2, pt3, nPoints=10):
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


def shiftLoopSet(loopSets, xS, yS):
    newLoopSet = []
    for loop in loopSets:
        newLoop = []
        for seg in loop:
            newSeg = [(x + xS, y + yS) for x, y in seg]
            newLoop.append(newSeg)
        newLoopSet.append(newLoop)
    return newLoopSet


def plotTextString(stringToPlot):
    fontPath = "/usr/share/cups/fonts/FreeMono.ttf"
    typeFace = Face(fontPath)
    typeFace.set_char_size(48 * 64)

    figure()
    startX, startY = 0, 0
    for char in stringToPlot:
        typeFace.load_char(char)
        loopz = unpackCharacter(typeFace.glyph)
        loopz = shiftLoopSet(loopz, startX, startY)
        startX += typeFace.glyph.advance.x
        startY += typeFace.glyph.advance.y
        plotLoopSets(loopz)
    axis("equal")
    show()
    close()


if __name__ == "__main__":
    plotTextString("The quick brown fox jumped over the lazy dogs.")
