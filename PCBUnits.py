import units.predefined

units.predefined.define_units()

inch = units.predefined.unit('inch')
mil = units.predefined.scaled_unit("mil", "inch", 0.001)
cm = units.predefined.unit("cm")
mm = units.predefined.unit("mm")
