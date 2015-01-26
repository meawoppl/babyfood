# Based on the data sheet from here:
# http://www.adafruit.com/datasheets/WS2812.pdf

from babyfood.pcb.PCBUnits import toMM
from babyfood.features.basic import CenteredRectangle, FilledCenteredRectangle, FilledCenteredCircle


class WS2812:
    _pinNumbers = [i + 1 for i in range(6)]
    _pinNames = ["DOUT", "DIN", "VCC", "", "VDD", "VSS"]

    @property
    def pinNumbers(self):
        return self._pinNumbers

    @property
    def pinNames(self):
        return self._pinNames

    def _getPadCenters(self):
        for x in [2.45, -2.45]:
            for y in [-1.6, 0, 1.6]:
                yield toMM(x), toMM(y)

    def _drawPads(self, pcb):
        h = toMM(1)
        w = toMM(1.5)
        pad = FilledCenteredRectangle(w, h)
        for x, y in self._getPadCenters():
            with pcb.transform.translation(x, y):
                pad.draw(pcb)

    def draw(self, pcb):
        outlineThickness = toMM(0.2)
        pcb.setActiveLayer("overlay")
        pcb.defineCircularAperature(outlineThickness)

        # Render the outline
        w = h = toMM(5) + (outlineThickness / 2)
        outline = CenteredRectangle(w, h)
        outline.draw(pcb)

        # Render the LED Center
        pcb.circle(0, 0, toMM(1.5))

        # Draw the pin1 marker
        fc = FilledCenteredCircle(toMM(0.25))
        loc = toMM(5) / 2 + 0.5
        with pcb.transform.translation(loc, -loc):
            fc.draw(pcb)

        # Render the pads and masks
        for layer in ["copper", "mask"]:
            pcb.setActiveLayer(layer)
            self._drawPads(pcb)
