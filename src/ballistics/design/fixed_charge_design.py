from typing import Optional

from attrs import frozen

from ..problem import FixedChargeProblem
from .base_design import BaseDesign


@frozen(kw_only=True)
class FixedChargeDesign(BaseDesign):
    charge_mass: Optional[float] = None
    charge_masses: list[float] | tuple[float, ...] = tuple()

    def set_up_problem(self, travel: float) -> FixedChargeProblem:
        base_problem = super().set_up_problem(travel=travel)
        return FixedChargeProblem.from_base_problem(
            base_problem=base_problem, charge_mass=self.charge_mass, charge_masses=self.charge_masses
        )
