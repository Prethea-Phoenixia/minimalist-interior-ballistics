from typing import Optional, Type

from attrs import field, frozen, asdict
from .. import DEFAULT_GUN_LOSS_FRACTION, DEFAULT_GUN_START_PRESSURE, DEFAULT_STEPS, DEFAULT_ACC
from ..charge import Propellant
from ..form_function import FormFunction
from ..problem import BaseProblem, PressureTarget


@frozen(kw_only=True)
class BaseDesign:
    name: str = field(default="")
    description: str = field(default="")
    family: str = field(default="")

    propellant: Optional[Propellant] = None
    propellants: list[Propellant] | tuple[Propellant, ...] = tuple()

    form_function: Optional[FormFunction] = None
    form_functions: list[FormFunction] | tuple[FormFunction, ...] = tuple()

    cross_section: float
    shot_mass: float
    loss_fraction: float = DEFAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE

    pressure_target: PressureTarget

    acc: float = DEFAULT_ACC
    n_intg: int = DEFAULT_STEPS

    def set_up_problem(self, travel: float) -> BaseProblem:
        return BaseProblem(**asdict(self, recurse=False), travel=travel)
