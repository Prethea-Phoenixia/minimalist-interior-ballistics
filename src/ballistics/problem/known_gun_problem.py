from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import frozen

from .. import DEFAULT_ACC, DEFAULT_STEPS
from .base_problem import BaseProblem

if TYPE_CHECKING:
    from ..gun import Gun
    from .pressure_target import PressureTarget


if TYPE_CHECKING:
    # these are required for pdoc
    from ..charge import FormFunction, Propellant


@frozen(kw_only=True)
class KnownGunProblem(BaseProblem):
    chamber_volume: float

    charge_mass: Optional[float] = None
    charge_masses: list[float] | tuple[float, ...] = tuple()

    def __attrs_post_init__(self):

        super().__attrs_post_init__()  # todo: test if this is needed.
        if self.charge_mass:
            object.__setattr__(self, "charge_masses", tuple([self.charge_mass]))

        if self.charge_masses:
            if len(self.charge_masses) != len(self.propellants):
                raise ValueError("charge_masses must have the same dimension as self.propellants and form_functions")
        else:
            raise ValueError("invalid parameters")

    def get_gun(
        self,
        *,
        reduced_burnrate: Optional[float] = None,
        reduced_burnrates: Optional[list[float] | tuple[float, ...]] = None,
        **kwargs,
    ) -> Gun:

        if reduced_burnrate:
            reduced_burnrates = tuple([reduced_burnrate])

        if reduced_burnrates:
            if len(reduced_burnrates) != len(self.propellants):
                raise ValueError(
                    "reduced_burnrates must have the same dimension as self.propellants, charge_masses and form_functions"
                )
        else:
            raise ValueError("invalid parameters.")

        return super().get_gun(
            charge_masses=self.charge_masses, chamber_volume=self.chamber_volume, reduced_burnrates=reduced_burnrates
        )

    def get_gun_developing_pressure(
        self,
        *,
        pressure_target: PressureTarget,
        reduced_burnrate_ratios: Optional[tuple[float, ...] | list[float]] = None,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        logging_preamble: str = "",
        **kwargs,
    ) -> Gun:

        return super().get_gun_developing_pressure(
            charge_masses=self.charge_masses,
            chamber_volume=self.chamber_volume,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
            logging_preamble=logging_preamble,
        )
