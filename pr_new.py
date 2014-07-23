import numpy as np
from itertools import product

dimensions = 5
gridSpacings = 0

phi = (1 + np.sqrt(5)) / 2

t = np.linspace(0, 2 * np.pi, dimensions + 1)[:-1]
basisVectors = np.vstack((np.cos(t), np.sin(t))).T * 2.0

shifts = np.array([2, 3, 5.1, 7, 11])
shifts[:] = 0

offsets = basisVectors * shifts[:, np.newaxis]
steps = np.arange(-gridSpacings, gridSpacings + 1)


def twoPointsToXYC(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    return (y2 - y1), (x1 - x2), (y1 * (x1 - x2)) - (x1 * (y1 - y2))


def generateGridline(n, basisVector, translation):
    # first point is easy.
    point1 = (n * basisVector) - translation

    # second point is from rotating the basis vector 90 degrees
    point2 = np.array([point1[0] + basisVector[1], point1[1] - basisVector[0]])

    return twoPointsToXYC(point1, point2)


pt1 = np.array([0, 0])
pt2 = np.array([1, 1])
pt3 = np.array([1, -1])


print(twoPointsToXYC(pt1, pt2))
print(twoPointsToXYC(pt1, pt3))
print(twoPointsToXYC(pt2, pt3))

print(generateGridline(3, pt2, pt1))

# 1 / 0

from pylab import axis, figure, plot, show
figure()

for d1, d2 in product(range(5), range(5)):
    if d2 <= d1:
        continue
    # Make and invert the matrix for this dimension pair

    print("Axis %i on %i" % (d1, d2))
    for s1, s2 in product(steps, steps):
        x1, y1, c1 = generateGridline(s1 + 1, basisVectors[d1, :], offsets[d1, :])
        x2, y2, c2 = generateGridline(s2 + 1, basisVectors[d2, :], offsets[d2, :])

        m = np.matrix([[x1, y1],
                       [x2, y2]])
        rhs = np.array([c1, c2])[:, np.newaxis]

        intersection = m.I * rhs

        # The intersection is the first point in the kite
        pt1 = np.array(intersection).flatten()

        plot([pt1[0]], [pt1[1]], 'bo', alpha=0.5)
        thisRhomb = []
        for off1, off2 in [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]:
            newPoint = pt1.copy()
            Scale = -1
            newPoint += off1 * basisVectors[d1, :] * Scale
            newPoint += off2 * basisVectors[d2, :] * Scale
            thisRhomb.append(newPoint)

        rhombArray = np.array(thisRhomb)
        color = "b" if (np.abs(d2 - d1) % 2) == 1 else "r"
        plot(rhombArray[:, 0], rhombArray[:, 1])

axis("equal")
show()
