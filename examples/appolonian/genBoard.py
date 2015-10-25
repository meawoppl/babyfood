import itertools, os

import numpy as np

from babyfood.pcb.PCBUnits import inch
from babyfood.pcb.OSHParkPCB import OSHParkPCB


def produceGasketPCB(csvFileName, outputFolderName):
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
    rs -= 0.01 * inch
    rs[rs < 0] = 0

    maxRIndex = rs.argmax()
    maxR = rs[maxRIndex]
    maxRX = xs[maxRIndex]
    maxRY = ys[maxRIndex]

    maxDrillSize = 0.260 * inch
    minDrillSize = 0.006 * inch

    pcb = OSHParkPCB(outputFolderName)

    # Sketch the board outline
    pcb.setActiveLayer("outline")
    pcb.defineCircularAperature(0.0)
    pcb.hintedCircle(maxRX, maxRY, maxR * 1.05)

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
    #pcb.visualize()


if __name__ == "__main__":
    produceGasketPCB("earHoops.csv", "~/bf/earhoops")
    produceGasketPCB("gasker.csv", "~/bf/gasket")
