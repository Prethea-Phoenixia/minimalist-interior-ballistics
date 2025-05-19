from __future__ import annotations

from attrs import frozen, asdict
from .base_design import BaseDesign
from ..gun import Gun
from ..problem import FixedVolumeProblem, PressureTarget


@frozen(kw_only=True)
class FixedVolumeDesign(BaseDesign):
    chamber_volume: float

    @classmethod
    def from_base_design(cls, base_design: BaseDesign, chamber_volume: float):
        return cls(**asdict(base_design, recurse=False), chamber_volume=chamber_volume)

    def set_up_problem(self, travel: float) -> FixedVolumeProblem:
        base_problem = super().set_up_problem(travel=travel)
        return FixedVolumeProblem.from_base_problem(base_problem=base_problem, chamber_volume=self.chamber_volume)

    def get_optimal_gun(
        self,
        velocity_target: float,
        pressure_target: PressureTarget,
        reduced_burnrate_ratios: tuple[float, ...] | list[float] = tuple([1]),
        charge_mass_ratios: list[float] | tuple[float, ...] = tuple([1]),
        max_calibers: int = 500,
    ) -> Gun:
        def f(travel: float) -> Gun:
            _, gun_opt, _ = self.set_up_problem(travel=travel).get_limiting_guns_at_pressure(
                pressure_target=pressure_target,
                reduced_burnrate_ratios=reduced_burnrate_ratios,
                charge_mass_ratios=charge_mass_ratios,
            )
            return gun_opt

        return self.get_optimal_gun_with_opt_func(
            func_opt_gun_for_travel=f, velocity_target=velocity_target, max_calibers=max_calibers
        )
