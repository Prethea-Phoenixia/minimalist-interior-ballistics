"""
This package is written to provide the user with a "minimalist" set of tools for
calculating and solving interior ballistic problems.
"""

from enum import Enum


class Significance(Enum):
    IGNITION = "ignition"
    START = "shot start"
    PEAK_PRESSURE = "max pressure"
    FRACTURE = "fracture"
    BURNOUT = "burnout"
    MUZZLE = "muzzle"
    INTERMEDIATE = "x"
    STEP = ""
    BOMB = "bomb"


_g_0 = 9.806
MAX_DT = 10e-3  # 10ms

DEFAULT_GUN_START_PRESSURE = 30e6
DFEAULT_GUN_LOSS_FRACTION = 0.05

AMBIENT_PRESSURE = 101325
"""
in Pa. The pressure value used in `ballistics.charge.Charge` to force a minimum level of combustion
rate.
"""

REDUCED_BURN_RATE_INITIAL_GUESS = 1.0
MINIMUM_BOMB_STATE_FREE_FRACTION = 0.1

# DEFAULT_GUN_MIN_GROSS_LOAD_DENSITY = 200
# DEFAULT_GUN_MAX_GROSS_LOAD_DENSITY = 1200
