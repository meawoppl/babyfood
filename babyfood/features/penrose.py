import numpy as np
from pylab import figure, plot, show


def plotSegments(segmentList):
    figure()
    for segment in segmentList:
        (xs, xe), (ys, ye) = segment
        plot([xs, ys], [xe, ye])

    show()


starters = np.linspace(0, 2 * np.pi, 6)[:-1]
segments = [((0, 0), (np.cos(t), np.sin(t))) for t in starters]

startingRing = []

angleIncrement = np.pi / 10

plotSegments(segments)


def magnitude(vec):
    return np.sqrt(np.dot(vec, vec))


def computeFill(pt1, pt2, pt3):
    # Figure out the small angle b/t 3 points
    a = pt1 - pt2
    b = pt3 - pt2
    angle = np.arccos(np.dot(a, b) / (magnitude(a) * magnitude(b)))
    angleInDeg = angle * (180 / np.pi)
    angleInTenths = angle / (np.pi / 5)

    print("Deg:", angleInDeg)
    print("Tenths:", angleInTenths)

    # Figure out which direction it is pointing
    # wrt to the origin
    m = (pt1 + pt3) / 2
    sign = -1 if (np.dot(m, pt2) > 0) else 1

    # if it is pointing inward, correct to the 
    # obtuse solid angle in question
    if sign == -1:
        angleInTenths = 10 - angleInTenths


testPoints = [np.array((np.cos(t), np.sin(t))) for t in starters]
for i in range(5):
    pt1 = testPoints[(i + 0) % 5]
    pt2 = np.zeros(2)
    pt3 = testPoints[(i + 1) % 5]
    computeFill(pt1, pt2, pt3)
