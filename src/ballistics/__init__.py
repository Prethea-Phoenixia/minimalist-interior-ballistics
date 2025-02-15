"""
This package is written to provide the user with a "minimalist" set of tools for
calculating and solving interior ballistic problems.
"""

import datetime
from enum import Enum

__version__ = datetime.datetime.now().strftime("%Y.%m.%d.%H")  # calendar versioning.


class Significance(Enum):
    IGNITION = "ignition"
    START = "shot start"
    PEAK_PRESSURE = "max pressure"
    FRACTURE = "fracture"
    BURNOUT = "burnout"
    MUZZLE = "muzzle"
    INTERMEDIATE = "x"
    STEP = "..."
    BOMB = "bomb"
    ADIABAT = "adiabat"


MAX_DT = 10e-3  # 10ms

DEFAULT_GUN_START_PRESSURE = 30e6
DEFAULT_GUN_LOSS_FRACTION = 0.05

AMBIENT_PRESSURE = 101325
"""
in Pa. The pressure value used in `ballistics.charge.Charge` to force a minimum level of combustion
rate.
"""

REDUCED_BURN_RATE_INITIAL_GUESS = 1.0

DEFAULT_ACC: float = 1e-3
DEFAULT_STEPS: int = 10
