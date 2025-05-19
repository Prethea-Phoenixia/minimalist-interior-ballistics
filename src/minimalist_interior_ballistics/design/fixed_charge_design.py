from __future__ import annotations

from attrs import frozen, asdict
from .base_design import BaseDesign
from ..gun import Gun
from ..problem import FixedChargeProblem, PressureTarget


@frozen(kw_only=True)
class FixedChargeDesign(BaseDesign):
    charge_mass: float = 0.0
    charge_masses: list[float] | tuple[float, ...] = tuple()

    @classmethod
    def from_base_design(
        cls,
        base_design: BaseDesign,
        charge_mass: float = 0.0,
        charge_masses: list[float] | tuple[float, ...] = tuple(),
    ):
        return cls(**asdict(base_design, recurse=False), charge_masses=charge_masses, charge_mass=charge_mass)

    def set_up_problem(self, travel: float) -> FixedChargeProblem:
        base_problem = super().set_up_problem(travel=travel)
        return FixedChargeProblem.from_base_problem(
            base_problem=base_problem, charge_mass=self.charge_mass, charge_masses=self.charge_masses
        )

    def get_optimal_gun(
        self,
        velocity_target: float,
        pressure_target: PressureTarget,
        reduced_burnrate_ratios: tuple[float, ...] | list[float] = tuple([1]),
        max_calibers: int = 500,
    ) -> Gun:
        def f(travel: float) -> Gun:
            _, gun_opt, _ = self.set_up_problem(travel=travel).get_limiting_guns_at_pressure(
                pressure_target=pressure_target, reduced_burnrate_ratios=reduced_burnrate_ratios
            )
            return gun_opt

        return self.get_optimal_gun_with_opt_func(
            func_opt_gun_for_travel=f, velocity_target=velocity_target, max_calibers=max_calibers
        )
