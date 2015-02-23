import os

import numpy as np

from babyfood.features.basic import CircularVia, FilledCenteredRectangle
from babyfood.components.ws2812 import WS2812
from babyfood.components.SMAResistor import SMAResistor
from babyfood.pcb.PCBUnits import toMM
from babyfood.pcb.OSHParkPCB import OSHParkPCB
from babyfood.homogenous import HomogenousTransform

home = os.path.expanduser("~")
pth = os.path.join(home, "bf", "tiny_turtle")
if not os.path.exists(pth):
    os.makedirs(pth)

pcb = OSHParkPCB(pth)
pcb.setActiveSide("top")

# Draw the board outline
pcb.setActiveLayer("outline")
h = toMM(30)
w2 = toMM(30)
w1 = toMM(50)

pcb.moveTo(-w1 / 2, -h / 2)
pcb.lineTo(w1 / 2, -h / 2)
pcb.lineTo(w1 / 2, -h / 2)
pcb.lineTo(w2 / 2, h / 2)
pcb.lineTo(-w2 / 2, h / 2)
pcb.lineTo(-w1 / 2, -h / 2)

# Draw the grounding via's
headerVia = CircularVia((2.54 / 2) - .1, 1.02 / 2)
midlineWidth = (w1 + w2) / 2
offset = (midlineWidth / 2)


def shrinkify(xys, percent):
    projector = HomogenousTransform.scaling(percent)
    xys[:] = projector.project(xys)

# Draw the power via's
vccCoords = np.array(((-w2 / 2, h / 2),
                      (-w1 / 2, -h / 2),
                      (+w1 / 2, -h / 2),
                      (+w2 / 2, h / 2))).T
groundCoords = vccCoords.copy()

shrinkify(groundCoords, 0.6)
shrinkify(vccCoords, 0.9)

for c in (vccCoords, groundCoords):
    for lin in c.T:
        xc, yc = lin[:]
        with pcb.transform.translation(xc, yc):
            headerVia.draw(pcb)
# MRG BUG NOTE: Circular via's set the active side to bottom. . .
pcb.setActiveSide("top")

# draw in the LED module
WS2812().draw(pcb)

# Connect the Grounding pads
pcb.setActiveLayer("copper")
pcb.defineCircularAperature(0.5)
pcb.moveTo(*groundCoords[:, 1])
pcb.lineTo(*groundCoords[:, 0])
pcb.lineTo(*groundCoords[:, 3])
pcb.lineTo(*groundCoords[:, 2])

# Connect the VCC pads
pcb.moveTo(*vccCoords[:, 0])
pcb.lineTo(*vccCoords[:, 1])
pcb.lineTo(*vccCoords[:, 2])
pcb.lineTo(*vccCoords[:, 3])


def drawJumperSet(pcb, size=1.5, spacing=1.7):
    solderJumperPad = FilledCenteredRectangle(toMM(size), toMM(size))

    for x in (-spacing, 0, +spacing):
        for y in (-spacing, 0, +spacing):
            with pcb.transform.translation(x, y):
                solderJumperPad.draw(pcb)

    pcb.defineCircularAperature(0.5)
    pcb.moveTo(-spacing, spacing)
    pcb.lineTo(spacing, spacing)

    pcb.moveTo(-spacing, -spacing)
    pcb.lineTo(spacing, -spacing)

    smallVia = CircularVia(0.6, 0.2)
    for x in (-spacing, 0, +spacing):
        with pcb.transform.translation(x, 0):
            smallVia.draw(pcb)

for layer in ("copper", "mask"):
    # draw the data spliters
    pcb.setActiveSide("top")
    pcb.setActiveLayer(layer)
    with pcb.transform.translation(0, -6):
        drawJumperSet(pcb)


pcb.setActiveSide("bottom")
pcb.setActiveLayer("copper")
dataJumpers = ((+1.7, -6),
               (+0.0, -6),
               (-1.7, -6))

scalar = 0.75
dataHeaders = ((+midlineWidth * scalar / 2, 0),
               (0, -h * scalar / 2),
               (-midlineWidth * scalar / 2, 0))

pcb.defineCircularAperature(0.3)
for dj, dh in zip(dataJumpers, dataHeaders):
    pcb.moveTo(*dj)
    pcb.lineTo(*dh)

    with pcb.transform.translation(*dh):
        headerVia.draw(pcb)

# Connect the data lines to the data jumpers
pcb.setActiveSide("top")
pcb.setActiveLayer("copper")

# DI
pcb.defineCircularAperature(0.3)
pcb.moveTo(2.45, 0)
pcb.lineTo(5, 0)
pcb.lineTo(5, -6 - 1.7)
pcb.lineTo(5, -6 - 1.7)
pcb.lineTo(1.7, -6 - 1.7)

# DO
pcb.moveTo(2.45, -1.6)
pcb.lineTo(4, -1.6)
pcb.lineTo(4, -6 + 1.7)
pcb.lineTo(4, -6 + 1.7)
pcb.lineTo(1.7, -6 + 1.7)

# Ground line
pcb.moveTo(-2.45, -1.6)
pcb.lineTo(-4, -1.6)
pcb.lineTo(-4, -15 * 0.9)

# Cap ground Line
pcb.moveTo(-2.45, -1.6)
pcb.lineTo(-0.88, -1.6)
pcb.lineTo(-0.88, 4)

# VCC line
pcb.moveTo(-2.45, 0)
pcb.lineTo(-4, 0)
pcb.lineTo(-4, 9)

# Bypass cap
c = SMAResistor("0805")
with pcb.transform.translation(0, 4.5):
    c.draw(pcb)

c = SMAResistor("0805")
with pcb.transform.translation(0, 6.5):
    c.draw(pcb)

# Connect the LED current supply
pcb.setActiveLayer("copper")
pcb.moveTo(2.45, 1.6)
pcb.lineTo(4, 1.6)
pcb.lineTo(4, 6.5)
pcb.lineTo(1.2, 6.5)

pcb.moveTo(4, 4.5)
pcb.lineTo(1.2, 4.5)

pcb.moveTo(-1.2, 6.5)
pcb.lineTo(-4, 6.5)



pcb.finalize()
pcb.visualize()
