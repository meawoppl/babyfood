import os
from itertools import product

from babyfood.tests.shared import GerbvTester, _quickTempFilePath
from babyfood.PCB import PCBArtist

sides = ["top", "bottom"]
layers = ["overlay", "copper", "mask"]


def _init_pcb_stack():
    art = PCBArtist()

    paths = []

    tempFolder = _quickTempFilePath()
    os.mkdir(tempFolder)
    # Init some realisticish layers
    for side, layerName in product(sides, layers):
        path = os.path.join(tempFolder, side + "_" + layerName + ".gbr")

        art.initializeGBRLayer(path, layerName, side)
        paths.append(path)

    # Do a drill layer too
    p = os.path.join(tempFolder, "drill.xln")
    art.initializeXLNLayer(p, "drill")
    paths.append(p)

    return art, paths


class GerberWriterTestCase(GerbvTester):
    def test_pcb_simple(self):
        art, paths = _init_pcb_stack()
        # Add some flashes + holes
        for side, layerName in product(sides, layers):
            art.setActiveLayer(layerName, side)
            art.defineCircularAperature(0.25)
            art.flashAt(0, 0)

        art.addHole(0, 0, 0.5)
        art.finalize()

        # Make sure the files don't turn up empty
        for p in paths:
            objCount = self._count_objects_in_file(p)
            self.assertEqual(objCount, 1)

    def test_pcb_translation(self):
        art, paths = _init_pcb_stack()
        # Add some flashes + holes
        for n, (side, layerName) in enumerate(product(sides, layers)):
            art.setActiveLayer(layerName, side)
            art.defineCircularAperature(0.25)

            with art.transform.translation(n, n):
                art.flashAt(0, 0)

        with art.transform.translation(-1, -1):
            art.addHole(0, 0, 0.25)

        art.finalize()

        # Make sure the files don't turn up empty
        for p in paths:
            objCount = self._count_objects_in_file(p)
            self.assertEqual(objCount, 1)

        folder, _ = os.path.split(paths[0])
        img = self._check_gerber_folder(folder)
        count = self._count_objects_in_img(img)

        self.assertEqual(count, len(paths))
