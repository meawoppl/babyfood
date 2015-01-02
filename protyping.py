# This is just some bullshitting about how
# The programmer <> PCB interaction might look

p = PCB()

# Component initialzation
r1 = SMAResistor(ohms = 2E6)
r2 = SMAResistor(ohms = 2E6)
r3 = SMAResistor(ohms = 2E6)
r4 = SMAResistor(ohms = 100)
ph = PinHeader(spacing = 0.1, pinCount=4)

ground = NamedNode("ground")

# PCB scale interactions
p.addComponent(r1)

with p.translate(200, 100):
    p.addComponent(r1)

# Indication of components linkages
r1[1] >> r2[2]
      >> r3[2]
      >> ground

ph[0] >> r2[2] >> ph[1] >> ground


# Artist interactions
class SMAResistor(PCBComponent):
    def __init__(self, *args):
        self.args = args

    def render(self, pcb):
        for x in [-4, 4]:
            with pcb.translate(x, 0):
                pad = PCBSquarePad()
                pad.render(pcb)


class SMASquarePad(PCBComponent):
    def __init__(length, width, *args, **kwargs):
        self.l, self.w = length, width

    def render(self, pcb):
        for layer in ["trace", "mask"]:
            pcb.setActiveLayer(layer)
            with pcb.polygon():
                hl, hw = self.l, self.w
                pbc.moveTo(-hl, hw)
                pbc.lineTo( hl, hw)
                pbc.lineTo( hl,-hw)
                pbc.lineTo(-hl,-hw)
                pbc.lineTo(-hl, hw)

