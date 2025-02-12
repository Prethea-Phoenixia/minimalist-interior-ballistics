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
    charge_masses: Optional[list[float] | tuple[float, ...]] = None

    def __attrs_post_init__(self):

        super().__attrs_post_init__()  # todo: test if this is needed.
        if self.propellant and self.form_function:
            object.__setattr__(self, "propellants", tuple([self.propellant]))
            object.__setattr__(self, "form_functions", tuple([self.form_function]))

        if self.propellants and self.form_functions:
            if len(self.propellants) != len(self.form_functions):
                raise ValueError("propellants and form_functions length mismatch")
        else:
            raise ValueError("invalid BaseProblem parameters")

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
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        logging_preamble: str = "",
        **kwargs,
    ) -> Gun:

        return super().get_gun_developing_pressure(
            charge_masses=self.charge_masses,
            chamber_volume=self.chamber_volume,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
            logging_preamble=logging_preamble,
        )
