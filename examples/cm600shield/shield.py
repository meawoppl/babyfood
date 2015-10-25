import os

import numpy as np

# from babyfood.features.basic import CircularVia, FilledCenteredRectangle
from babyfood.components.ThruHole import ST_15KE22CA, ST_15KE220CA, THTwoLead
from babyfood.components.PinHeader import JSTConnector
from babyfood.pcb.PCBUnits import toMM
from babyfood.pcb.OSHParkPCB import OSHParkPCB
from babyfood.features.basic import SquareVia

home = os.path.expanduser("~")
pth = os.path.join(home, "bf", "cm600")
if not os.path.exists(pth):
    os.makedirs(pth)

pcb = OSHParkPCB(pth)
pcb.setActiveSide("top")


# Constants from the spec sheet
# http://www.pwrx.com/pwrx/docs/cm600ha24h.pdf
A = toMM(110)
E = toMM(40)
G = toMM(29)
J = toMM(25)
L = toMM(21)
N = toMM(17.5)
P = toMM(15.5)
Q = toMM(13)
R = toMM(12.5)
S = toMM(11.5)
Z = toMM(3.04)

padSize = toMM(9)


# The bolt-on interfaces
sv = SquareVia(padSize, padSize, toMM(4.5 / 2))

with pcb.transform.translation(-L, -E / 2):
    sv.draw(pcb)

with pcb.transform.translation(-L - Q, E / 2):
    sv.draw(pcb)


# Draw the board outline
pcb.setActiveLayer("outline")
margin = toMM(1)
leftEdge = -(Q + L + (padSize / 2) + margin)
topEdge = (E / 2) + (padSize / 2) + margin
bottomEdge = -((E / 2) + (padSize / 2) + margin)
farRight = A / 2
pcb.moveTo(leftEdge, topEdge)
pcb.lineTo(leftEdge, bottomEdge)
pcb.lineTo(farRight, bottomEdge)
pcb.lineTo(farRight, topEdge)
pcb.lineTo(leftEdge, topEdge)


# Inner box
margin = toMM(0.5)
boxTop = P + margin
boxLeft = -S - margin
boxRight = -S + J + Z + J + margin
boxBottom = -R - margin

pcb.moveTo(boxLeft, boxTop)
pcb.lineTo(boxLeft, boxBottom)
pcb.lineTo(boxRight, boxBottom)
pcb.lineTo(boxRight, boxTop)
pcb.lineTo(boxLeft, boxTop)


# Draw the big TVS string
c = ST_15KE220CA()

stretch = 59.5 / 2
with pcb.transform.translation(8.5, 21):
    for x in np.linspace(-stretch, stretch, 5):
        with pcb.transform.translation(x, 0):
            with pcb.transform.rotation(0.15):
                c.draw(pcb)

# G -> C TVS and 0.1 ohm resistor
c = ST_15KE22CA()
for i in [-3, 3]:
    with pcb.transform.translation(-L + i, 0):
        with pcb.transform.rotation(3.1415 / 2):
            c.draw(pcb)

# Resistor and diode pair
dr = THTwoLead(toMM(12), toMM(0.75), toMM(0.65))

for xpos in [-30, -35]:
    with pcb.transform.translation(xpos, -10):
        with pcb.transform.rotation(3.1415 / 2):
            c.draw(pcb)

# JST Connectors
jst = JSTConnector(2)
with pcb.transform.rotation(-3.1415 / 2):
    with pcb.transform.translation(0, -32):
        with pcb.transform.translation(-4, 0):
            jst.draw(pcb)
        with pcb.transform.translation(-11, 0):
            jst.draw(pcb)


# Connect teh JST -> JST
pcb.setActiveSide("top")
pcb.setActiveLayer("copper")
pcb.defineCircularAperature(1.0)
pcb.moveTo(-32, 12)
pcb.lineTo(-30, 12)
pcb.lineTo(-30, 5)
pcb.lineTo(-32, 5)


pcb.moveTo(-32, 10)
pcb.lineTo(-34, 10)
pcb.lineTo(-34, 3)
pcb.lineTo(-32, 3)

# Resister/diode to gate
pcb.moveTo(-35, -17.5)
pcb.lineTo(-21, -17.5)

# JST -> r/d
pcb.moveTo(-32, 3)
pcb.lineTo(-30, -2)

pcb.moveTo(-35, -2.5)
pcb.lineTo(-30, -2.5)

# JST -> 0.1 Ohm
pcb.moveTo(-30, 5)
pcb.lineTo(-24, -7)

#
pcb.moveTo(-L - Q, E / 2)
pcb.lineTo(-24, 7.5)
pcb.lineTo(-18, 7.5)


pcb.moveTo(-L, -E / 2)
pcb.lineTo(-18, -7.5)

pcb.finalize()
pcb.visualize()
