import unittest
from babyfood.components.ABC import AbstractSMAComponent, AbstractTHComponent
from babyfood.pcb.PCBBase import PCBArtist


class FakeTHComponent(AbstractTHComponent):
    def __init__(self):
        AbstractTHComponent.__init__(self)
        self.addPin(1, (1, 0), "+")
        self.addPin(2, (-1, 0), "-")


class FakeSMAComponent(AbstractSMAComponent):
    def __init__(self):
        AbstractSMAComponent.__init__(self)
        self.addPad(1, (1, 0), "=")
        self.addPad(2, (-1, 0), ">")


class THComponentsTestCase(unittest.TestCase):
    def test_th_basic(self):
        fc = FakeTHComponent()

        cNames = fc.getConnectorNames()
        ids = fc.getConnectorIDs()
        xys = fc.getConnectorCenters()

        self.assertEqual(len(cNames), 2)
        self.assertEqual(len(ids), 2)
        self.assertEqual(len(xys), 2)

    def test_th_translated(self):
        art = PCBArtist()
        fc = FakeTHComponent()

        with art.transform.translation(1, 0):
            fc.place(art)

        fc = FakeSMAComponent()


class SMAComponentsTestCase(unittest.TestCase):
    def test_sma_dumb(self):
        FakeSMAComponent()
