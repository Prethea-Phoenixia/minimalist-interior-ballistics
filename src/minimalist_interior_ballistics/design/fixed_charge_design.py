from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from math import pi
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

    def get_optimal_gun(
        self,
        velocity_target: float,
        reduced_burnrate_ratios: tuple[float, ...] | list[float] = tuple([1]),
        max_calibers: int = 1000,
    ) -> Gun:
        caliber = (4 * self.cross_section / pi) ** 0.5

        def f(travel: float) -> Gun:
            _, gun_opt, _ = self.set_up_problem(travel=travel).get_limiting_guns_at_pressure(
                pressure_target=self.pressure_target, reduced_burnrate_ratios=reduced_burnrate_ratios
            )
            return gun_opt

        def fmv(travel: float) -> float:
            gun = f(travel=travel)
            return gun.to_travel(n_intg=self.n_intg, acc=self.acc).muzzle_velocity - velocity_target

        max_travel = max_calibers * caliber
        if fmv(travel=max_travel) < 0:
            raise ValueError(f"velocity cannot be achieved out to {max_calibers:.0f} calibers.")
        counterpoint = max_travel * 0.5
        while fmv(counterpoint) >= 0:
            counterpoint *= 0.5

        travel, _ = dekker(f=lambda x: fmv(x), x_0=counterpoint, x_1=max_travel, tol=counterpoint * self.acc)

        return f(travel=travel)
