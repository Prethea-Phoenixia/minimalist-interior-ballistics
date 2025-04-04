"""
.. include:: ./quickstart.md

# API Documentation
"""

import datetime
from enum import Enum

__version__ = datetime.datetime.now().strftime("%Y.%m.%d.%H")
"""
minimalist-interior-minimalist_interior_ballistics currently uses a calendar versioning scheme, as development
is very much ongoing, large parts of the interface and implementation may be subjected to 
modification without regard for backwards compatibility.
"""


class Significance(str, Enum):
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


MAX_DT: float = 1e-3
"""
in Seconds. This is both initial and the maximum time step the program will attempt to use
to integrate interior minimalist_interior_ballistics trajectories.
"""

DEFAULT_GUN_START_PRESSURE: float = 30e6
DEFAULT_GUN_LOSS_FRACTION: float = 0.05

AMBIENT_PRESSURE: float = 101325
"""
in Pa. The pressure value used in `minimalist_interior_ballistics.charge.Charge` to force a minimum level of combustion
rate. This prevents edge cases from taking excessive time to return. 
"""

REDUCED_BURN_RATE_INITIAL_GUESS = 1.0


DEFAULT_ACC: float = 1e-3
DEFAULT_STEPS: int = 10
"""
Sets the default value for `acc` and `n_intg`, whereever numerical techniques are used.
"""
