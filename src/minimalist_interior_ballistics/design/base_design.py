from __future__ import annotations

from typing import Optional, Callable, TYPE_CHECKING

from attrs import field, frozen, asdict, fields, Attribute
from .. import DEFAULT_GUN_LOSS_FRACTION, DEFAULT_GUN_START_PRESSURE, DEFAULT_STEPS, DEFAULT_ACC
from ..gun import Gun
from ..problem import BaseProblem
from ..num import dekker
from math import pi


from ..charge import Propellant
from ..form_function import FormFunction


@frozen(kw_only=True, auto_attribs=True)
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

    acc: float = DEFAULT_ACC
    n_intg: int = DEFAULT_STEPS

    def set_up_problem(self, travel: float) -> BaseProblem:

        def basedesign_fields_filter(attr: Attribute, _) -> bool:
            if attr in fields(BaseDesign):
                return True
            return False

        return BaseProblem(**asdict(self, recurse=False, filter=basedesign_fields_filter), travel=travel)

    def get_optimal_gun_with_opt_func(
        self, func_opt_gun_for_travel: Callable[[float], Gun], velocity_target: float, max_calibers: int
    ) -> Gun:

        def func_mv(travel: float) -> float:
            gun = func_opt_gun_for_travel(travel)
            return gun.to_travel(n_intg=self.n_intg, acc=self.acc).muzzle_velocity - velocity_target

        max_travel = max_calibers * (4 * self.cross_section / pi) ** 0.5
        if func_mv(travel=max_travel) < 0:
            raise ValueError(f"velocity cannot be achieved out to {max_calibers:.0f} calibers.")

        ul = max_travel
        ll = max_travel * 0.5
        while fmvll := func_mv(ll) >= 0:
            if fmvll > 0:
                ul = ll
            ll *= 0.5

        opt_travel, _ = dekker(f=lambda x: func_mv(x), x_0=ll, x_1=ul, tol=ll * self.acc)

        return func_opt_gun_for_travel(opt_travel)
