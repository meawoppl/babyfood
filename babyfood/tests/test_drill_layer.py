from babyfood.layers.DrillLayer import DrillLayer
from babyfood.tests.shared import GerbvTester, _quickTempFilePath


class GerberWriterTestCase(GerbvTester):
    def test_drill_empty(self):
        xlnFilePath = _quickTempFilePath(".xln")
        xw = DrillLayer(xlnFilePath)
        xw.finalize()
        self._check_gerber_file(xlnFilePath)
