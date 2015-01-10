from babyfood.layers.DrillLayer import DrillLayer
from babyfood.tests.shared import GerbvTester, _quickTempFilePath


class DrillWriterTestCase(GerbvTester):
    def test_drill_simple(self):
        xlnFilePath = _quickTempFilePath(".xln")
        xw = DrillLayer(xlnFilePath)
        xw.addHole(0, 0, 0.1)
        xw.finalize()
        self._check_gerber_file(xlnFilePath)

    def test_drill_multiple(self):
        xlnFilePath = _quickTempFilePath(".xln")
        xw = DrillLayer(xlnFilePath)

        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                xw.addHole(x, y, 0.1)
        xw.finalize()
        count = self._count_objects_in_file(xlnFilePath)
        self.assertEqual(count, 9)
