import os

import numpy as np

from babyfood import OSHParkPCB


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

# Rescale everything to mave a max diameter of 3in
rescalar = (25.4) / (2 * maxR)
rs *= rescalar
xs *= rescalar
ys *= rescalar
rs -= 0.05 * 2.54

maxRIndex = rs.argmax()
maxR = rs[maxRIndex]
maxRX = xs[maxRIndex]
maxRY = ys[maxRIndex]

maxDrillSize = 0.260 * 25.4
minDrillSize = 0.006 * 25.4

pcb = OSHParkPCB("appolonian")

pcb.setActiveLayer("outline")

# Draw all the full circle layers
for side in ("top", "bottom"):
    for layer in ["mask", "copper"]:
        pcb.setActiveLayer(layer, side)
        with pcb.polygonMode():
            pcb.circle(0, 0, maxR)


# Largest drill is 0.1 in
# Similarly cutout tool diameter is 0.1 in
# Do some pruning into drills/mechanical routing steps
for r, x, y in zip(rs, xs, ys):
    if r == maxR:
        print("Skipped max R")
        continue
    if r < minDrillSize:
        # Skip below minimum drill
        continue
    if r > maxDrillSize:
        pcb.setActiveLayer("outline")
        pcb.hintedCircle(x, y, r)
    else:
        pcb.addHole(r, x, y)
