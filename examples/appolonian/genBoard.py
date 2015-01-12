import itertools, os

import numpy as np

from babyfood.pcb.OSHParkPCB import OSHParkPCB


# This is a hack-around to support OSH park,
# which determines board bounds by looking at the
# raw coordinate data, and will get confused by a fully
# circular board
def cisDegree(angleInDeg, r=1):
    x = np.cos((np.pi / 180) * angleInDeg) * r
    y = np.sin((np.pi / 180) * angleInDeg) * r
    return x, y


csvFilename = os.path.join(os.path.split(__file__)[0], "gasket.csv")

# Load the csv file of gasket centers and radii
rs, xs, ys = np.loadtxt(csvFilename, skiprows=1, delimiter=",").T

# Radaii can be negative (which does make sense really!)
rs = np.abs(rs)

# Find the biggest circle
maxR = rs.max()
print(maxR)
print(rs)

# Rescale everything to mave a max diameter of 3in
rescalar = (25.4) / (2 * maxR)
rs *= rescalar
xs *= rescalar
ys *= rescalar
rs -= 0.01 * 2.54
rs[rs < 0] = 0

maxRIndex = rs.argmax()
maxR = rs[maxRIndex]
maxRX = xs[maxRIndex]
maxRY = ys[maxRIndex]

maxDrillSize = 0.260 * 2.54
minDrillSize = 0.006 * 2.54

pcb = OSHParkPCB("appolonian")

# Sketch the board outline
pcb.setActiveLayer("outline")
pcb.defineCircularAperature(0.0)
pcb.hintedCircle(0, 0, maxR * 1.05)


# Draw all the filled circle layers
for side, layer in itertools.product(("top", "bottom"), ("mask", "copper")):
    pcb.setActiveLayer(layer, side)
    with pcb.polygonMode():
        pcb.defineCircularAperature(0.0)
        pcb.circle(0, 0, maxR * 1.05)


# Largest drill is 0.1 in
# Similarly cutout tool diameter is 0.1 in
# Do some pruning into drills/mechanical routing steps
for r, x, y in zip(rs, xs, ys):
    print(r, x, y)
    if r == maxR:
        continue
    if r < minDrillSize:
        # Skip below minimum drill
        continue
    if r > maxDrillSize:
        pcb.setActiveLayer("outline")
        pcb.defineCircularAperature(0.0)
        pcb.circle(x, y, r)

        pcb.setActiveLayer("overlay", "top")
        pcb.defineCircularAperature(0.0)
        pcb.circle(x, y, r * 0.75)

        pcb.setActiveLayer("overlay", "bottom")
        pcb.defineCircularAperature(0.0)
        pcb.circle(x, y, r * 0.75)

    else:
        pcb.addHole(x, y, r * 2)

pcb.finalize()
pcb.visualize()
