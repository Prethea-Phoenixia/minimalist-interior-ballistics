from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import frozen, asdict
from ..gun import Gun
from .base_problem import BaseProblem, accepts_reduced_burnrate
from .pressure_target import PressureTarget

if TYPE_CHECKING:
    # these are required for pdoc to locate the references
    # noinspection PyUnresolvedReferences
    from ..charge import Propellant

    # noinspection PyUnresolvedReferences
    from ..form_function import FormFunction


@frozen(kw_only=True)
class KnownGunProblem(BaseProblem):
    chamber_volume: float
    charge_mass: Optional[float] = None
    charge_masses: list[float] | tuple[float, ...] = tuple()

    @classmethod
    def from_base_problem(
        cls,
        base_problem: BaseProblem,
        chamber_volume: float,
        charge_mass: Optional[float] = None,
        charge_masses: list[float] | tuple[float, ...] = tuple(),
    ) -> KnownGunProblem:
        return cls(
            **asdict(base_problem, recurse=False),
            chamber_volume=chamber_volume,
            charge_mass=charge_mass,
            charge_masses=charge_masses,
        )

    @accepts_reduced_burnrate
    def get_gun(self, reduced_burnrates: tuple[float, ...], **kwargs) -> Gun:

        return super().get_gun(
            charge_mass=self.charge_mass,
            charge_masses=self.charge_masses,
            chamber_volume=self.chamber_volume,
            reduced_burnrates=reduced_burnrates,
        )

    def get_gun_at_pressure(
        self,
        pressure_target: PressureTarget,
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
        **kwargs,
    ) -> Gun:

        return super().get_gun_at_pressure(
            charge_mass=self.charge_mass,
            charge_masses=self.charge_masses,
            chamber_volume=self.chamber_volume,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            pressure_target=pressure_target,
        )
