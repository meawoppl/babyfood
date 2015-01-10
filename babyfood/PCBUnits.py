from pint import UnitRegistry

_unitRegistry = UnitRegistry()
_unitRegistry.define("mil = inch / 1000")


def _toUnit(floatOrUnited, unitName):
    try:
        return floatOrUnited.to(unitName)
    except:
        return _unitRegistry.Quantity(floatOrUnited, unitName)

inch = lambda f: _toUnit(f, 'inch')
mil = lambda f: _toUnit(f, "mil")
cm = lambda f: _toUnit(f, "cm")
mm = lambda f: _toUnit(f, "mm")
