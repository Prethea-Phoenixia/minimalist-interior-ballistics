from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import frozen
from .. import DEFAULT_ACC, DEFAULT_STEPS, Significance
from .base_design import BaseDesign
from ..gun import Gun
from ..num import dekker, gss_max
from ..problem import FixedChargeProblem


@frozen(kw_only=True)
class FixedChargeDesign(BaseDesign):
    charge_mass: Optional[float] = None
    charge_masses: list[float] | tuple[float, ...] = tuple()

    def set_up_problem(self, travel: float) -> FixedChargeProblem:
        base_problem = super().set_up_problem(travel=travel)
        return FixedChargeProblem.from_base_problem(
            base_problem=base_problem, charge_mass=self.charge_mass, charge_masses=self.charge_masses
        )

    # def get_optimal_gun(
    #     self,
    #     velocity_target: float,
    #     reduced_burnrate_ratios: Optional[tuple[float, ...] | list[float]] = None,
    #     n_intg: int = DEFAULT_STEPS,
    #     acc: float = DEFAULT_ACC,
    # ) -> Gun:

    # def f(travel: float) -> Gun:
    #     _, gun_opt, _ = self.set_up_problem(travel=travel).get_guns_at_pressure(
    #         pressure_target=self.pressure_target, n_intg=n_intg, acc=acc
    #     )
    #     return gun_opt

    # test_gun = f(1.0)

    # asymptotic_velocity = f(1.0).asymptotic_velocity

    # if velocity_target > asymptotic_velocity:
    #     raise ValueError("velocity cannot be achieved with specified charge:mass.")

    # def fmv(travel: float) -> float:
    #     gun = f(travel=travel)
    #     return gun.to_travel(n_intg=n_intg, acc=acc).muzzle_velocity - velocity_target

    # guess = 1.0
    # if fmv(guess) < 0:
    #     counterpoint = guess * 2
    #     while fmv(counterpoint) < 0:
    #         counterpoint *= 2

    # else:
    #     counterpoint = guess * 0.5
    #     while fmv(counterpoint) >= 0:
    #         counterpoint *= 0.5

    # travel, _ = dekker(f=lambda x: fmv(x), x_0=guess, x_1=counterpoint, tol=min(guess, counterpoint) * acc)

    # return f(travel=travel)
