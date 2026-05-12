"""Unit constants used by ProChem core and analysis code."""

from __future__ import annotations

ANGSTROM = 1.0
FEMTOSECOND = 1.0
EV = 1.0

ANGSTROM_TO_METER = 1.0e-10
FEMTOSECOND_TO_SECOND = 1.0e-15

ANGSTROM_PER_FS_TO_M_PER_S = ANGSTROM_TO_METER / FEMTOSECOND_TO_SECOND

# Legacy ProChem conversion used by the old processing table.
KINETIC_ENERGY_FACTOR = 2 * 9.65 * 1000

