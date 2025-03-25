from typing import TYPE_CHECKING, Optional

from attrs import frozen
from ballistics import DEFAULT_ACC, DEFAULT_STEPS, Significance
from ballistics.design.base_design import BaseDesign
from ballistics.gun import Gun
from ballistics.num import dekker, gss_max
from ballistics.problem import FixedChargeProblem


@frozen(kw_only=True)
class FixedChargeDesign(BaseDesign):
    charge_mass: Optional[float] = None
    charge_masses: list[float] | tuple[float, ...] = tuple()

    velocity_target: float

    def set_up_problem(self, travel: float) -> FixedChargeProblem:
        base_problem = super().set_up_problem(travel=travel)
        return FixedChargeProblem.from_base_problem(
            base_problem=base_problem, charge_mass=self.charge_mass, charge_masses=self.charge_masses
        )

    def get_optimal_gun(
        self,
        velocity_target: float,
        reduced_burnrate_ratios: Optional[tuple[float, ...] | list[float]] = None,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
    ) -> Gun:

        def f(travel: float) -> Gun:
            _, gun_opt, _ = self.set_up_problem(travel=travel).get_guns_at_pressure(
                pressure_target=self.pressure_target, n_intg=n_intg, acc=acc
            )
            return gun_opt

        asymptotic_velocity = f(0.0).asymptotic_velocity

        if velocity_target > asymptotic_velocity:
            raise ValueError("velocity cannot be achieved with specified charge:mass.")
