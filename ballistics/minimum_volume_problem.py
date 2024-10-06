from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import DEFAULT_GUN_START_PRESSURE, DFEAULT_GUN_LOSS_FRACTION
from .charge import Propellant
from .matching_problem import MatchingProblem
from .pressure_target import PressureTarget

if TYPE_CHECKING:
    from .form_function import FormFunction


logger = logging.getLogger(__name__)
