from pint import UnitRegistry

_unitRegistry = UnitRegistry()
_unitRegistry.define("mil = inch / 1000")


def _toUnit(floatOrUnited, unitName):
    try:
        return floatOrUnited.to(unitName).magnitude
    except:
        return _unitRegistry.Quantity(floatOrUnited, unitName).magnitude

toInch = lambda f: _toUnit(f, 'inch')
toMM = lambda f: _toUnit(f, 'inch')
inch = _unitRegistry.inch
mil = _unitRegistry.mil
cm = _unitRegistry.cm
mm = _unitRegistry.mm
