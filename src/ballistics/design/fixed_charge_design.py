from typing import Optional

from attrs import frozen

from .. import DEFAULT_ACC, DEFAULT_STEPS, Significance
from ..problem import FixedChargeProblem
from .base_design import BaseDesign


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

    # def get_optimal_gun(
    #     self,
    #     reduced_burnrate_ratios: Optional[tuple[float, ...] | list[float]] = None,
    #     velocity_target: Optional[float] = None,
    #     n_intg: int = DEFAULT_STEPS,
    #     acc: float = DEFAULT_ACC,
    # ) -> Gun:

    #     def f(x: float) -> float:
    #         fcp = self.set_up_problem(travel=x)
    #         gun_min, gun_opt, gun_max = fcp.solve_chamber_volume_at_pressure_for_velocity(
    #             pressure_target=self.pressure_target,
    #             reduced_burnrate_ratios=reduced_burnrate_ratios,
    #             n_intg=n_intg,
    #             acc=acc,
    #         )

    #         return gun_opt.to_travel(n_intg=n_intg, acc=acc).muzzle_velocity - self.velocity_target
