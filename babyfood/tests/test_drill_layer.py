from babyfood.layers.DrillLayer import DrillLayer
from babyfood.tests.shared import GerbvTester, _quickTempFilePath


class DrillWriterTestCase(GerbvTester):
    def test_drill_simple(self):
        xlnFilePath = _quickTempFilePath(".xln")
        xw = DrillLayer(xlnFilePath)
        xw.addHole(0, 0, 0.1)
        xw.finalize()
        self._check_gerber_file(xlnFilePath)
