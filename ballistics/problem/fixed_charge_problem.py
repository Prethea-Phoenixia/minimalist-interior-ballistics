from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Tuple

from attrs import frozen

from .. import (DEFAULT_GUN_START_PRESSURE, DFEAULT_GUN_LOSS_FRACTION,
                MINIMUM_BOMB_STATE_FREE_FRACTION)
from ..charge import Charge, Propellant
from ..gun import Gun
from ..num import dekker
from .pressure_target import PressureTarget

if TYPE_CHECKING:
    from ..form_function import FormFunction


logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class FixedChargeProblem:
    propellant: Propellant
    form_function: FormFunction

    cross_section: float
    shot_mass: float
    charge_mass: float
    travel: float
    loss_fraction: float = DFEAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE

    def get_test_gun(self, reduced_burnrate: float, chamber_volume: float) -> Gun:
        charge = Charge.from_propellant(
            reduced_burnrate=reduced_burnrate,
            propellant=self.propellant,
            form_function=self.form_function,
        )

        gun = Gun(
            cross_section=self.cross_section,
            shot_mass=self.shot_mass,
            charge_mass=self.charge_mass,
            charge=charge,
            chamber_volume=chamber_volume,
            loss_fraction=self.loss_fraction,
            start_pressure=self.start_pressure,
        )
        return gun

    def get_chamber_volume_limits(
        self, pressure_target: PressureTarget, acc: float, logging_preamble: str = ""
    ) -> Tuple[float, float]:
        """
        find the range of valid chamber volume

        Parameters
        ----------
        pressure_target, acc: `ballistics.problem.pressure_target.PressureTarget`, float
            see `FixedVolumeProblem.solve_reduced_burn_rate` for more information.

        Returns
        -------
        lower_limit, upper_limit: float

        Notes
        -----
        The upper limit is determined to ensure minimum free fraction for the bomb case.

        The lower limit is such that the pressure specification may be achieved in the
        bomb case. Choice of the more conservative solution ensures valid (finite) burn
        rate if it were to be used.

        For more explanation of the rationale, reference
        `ballistics.problem.fixed_volume_problem.FixedVolumeProblem.get_charge_mass_limit`.

        """

        logger.info(logging_preamble + "VOLUME LIMIT")
        logger.info(logging_preamble + f"{pressure_target.describe()} ->")

        def f_ff(chamber_volume: float) -> float:
            test_gun = self.get_test_gun(reduced_burnrate=1, chamber_volume=chamber_volume)
            return test_gun.bomb_free_fraction - MINIMUM_BOMB_STATE_FREE_FRACTION

        chamber_min_volume = self.charge_mass / self.propellant.density

        bound = chamber_min_volume
        while f_ff(bound) < 0:
            bound *= 2

        lower_limit = max(
            dekker(f=f_ff, x_0=chamber_min_volume, x_1=bound, tol=chamber_min_volume * acc)
        )

        def f_p(chamber_volume: float) -> float:
            test_gun = self.get_test_gun(reduced_burnrate=1, chamber_volume=chamber_volume)
            test_gun_bomb_pressure = pressure_target.retrieve_from(test_gun.get_bomb_state())
            return test_gun_bomb_pressure - pressure_target.value

        bound = lower_limit
        while f_p(bound) > 0:
            bound *= 2

        upper_limit = min(dekker(f=f_p, x_0=lower_limit, x_1=bound, tol=chamber_min_volume * acc))

        logger.info(
            logging_preamble
            + f"-> chamber from {lower_limit * 1e3:.2f} L to {upper_limit * 1e3:.2f} L"
        )
        logger.info(logging_preamble + "END")
        return lower_limit, upper_limit
