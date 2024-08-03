"""
This package is written to provide the user with a "minimalist" set of tools for
calculating and solving interior ballistic problems.
"""

from enum import Enum


class Significance(Enum):
    PEAK_PRESSURE = "max pressure"
    FRACTURE = "fracture"
    BURNOUT = "burnout"
    MUZZLE = "muzzle"
    INTERMEDIATE = "x"
    START = "start"
    STEP = ""


_g_0 = 9.806
MAX_DT = 10e-3  # 10ms
DEFAULT_LOAD_DENSITY = 0.2e3
DEFAULT_IGNITION_PRESSURE = 100 * _g_0 / 1e-4
