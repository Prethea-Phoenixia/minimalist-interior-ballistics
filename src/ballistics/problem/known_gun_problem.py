from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import frozen

from .. import DEFAULT_ACC, DEFAULT_STEPS
from .base_problem import BaseProblem

if TYPE_CHECKING:
    from ..gun import MonoChargeGun
    from .pressure_target import PressureTarget


@frozen(kw_only=True)
class KnownGunProblem(BaseProblem):
    chamber_volume: float
    charge_mass: float

    def get_gun(self, *, reduced_burnrate: float, **kwargs) -> MonoChargeGun:
        return super().get_gun(
            charge_mass=self.charge_mass,
            chamber_volume=self.chamber_volume,
            reduced_burnrate=reduced_burnrate,
        )

    def get_gun_developing_pressure(
        self,
        *,
        pressure_target: PressureTarget,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        logging_preamble: str = "",
        **kwargs,
    ) -> MonoChargeGun:

        return super().get_gun_developing_pressure(
            charge_mass=self.charge_mass,
            chamber_volume=self.chamber_volume,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
            logging_preamble=logging_preamble,
        )
