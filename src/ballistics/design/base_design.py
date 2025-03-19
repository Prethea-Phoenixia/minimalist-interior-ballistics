from typing import Optional, Type

from attrs import field, frozen

from .. import DEFAULT_GUN_LOSS_FRACTION, DEFAULT_GUN_START_PRESSURE
from ..charge import Propellant
from ..form_function import FormFunction
from ..problem import PressureTarget
from ..problem.base_problem import BaseProblem


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

    velocity_target: float
    pressure_target: PressureTarget

    def set_up_problem(self, travel: float) -> BaseProblem:
        return BaseProblem(
            name=self.name,
            description=self.description,
            family=self.family,
            propellant=self.propellant,
            propellants=self.propellants,
            form_function=self.form_function,
            form_functions=self.form_functions,
            cross_section=self.cross_section,
            shot_mass=self.shot_mass,
            loss_fraction=self.loss_fraction,
            start_pressure=self.start_pressure,
            travel=travel,
        )
