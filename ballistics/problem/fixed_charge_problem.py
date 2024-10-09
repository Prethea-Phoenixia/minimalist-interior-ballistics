from __future__ import annotations

import logging
from typing import Tuple

from attrs import frozen

from .. import MINIMUM_BOMB_STATE_FREE_FRACTION, Significance
from ..charge import Charge
from ..gun import Gun
from ..num import dekker
from .base_problem import BaseProblem
from .pressure_target import PressureTarget

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class FixedChargeProblem(BaseProblem):

    charge_mass: float

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
            + f"-> chamber from {lower_limit * 1e3:.3f} L to {upper_limit * 1e3:.3f} L"
        )
        logger.info(logging_preamble + "END")
        return lower_limit, upper_limit

    def solve_reduced_burn_rate_for_volume_at_pressure(
        self,
        *,
        chamber_volume: float,
        pressure_target: PressureTarget,
        n_intg: int,
        acc: float,
        logging_preamble: str = "",
        **kwargs,
    ) -> Gun:
        """
        solves the reduced burn rate such that the peak pressure developed in bore
        matches the desired value. This is the outer, user facing function that validates
        the input by checking against the calculated chamber volume limits. Implementation
        is instead under `BaseProblem.solve_reduced_burn_rate_at_pressure` method.

        Parameters
        ----------
        chamber_volume: float
            volume of the chamber.
        pressure_target: float, `ballistics.problem.pressure_target.PressureTarget`
            the pressure to target, along with its point-of-measurement.
        n_intg, acc: int, float
            parameter passed to `ballistics.gun.Gun.to_burnout`. In addition, `acc`
            specifies the relative accuracy to which the reduced burn-rate is solved to,
            using an iterative procedure.

        Raises
        ------
        ValueError
            if the specified charge mass is either too low or too high for this
            gun design.

        Returns
        -------
        gun: `ballistics.gun.Gun` object
            the gun corresponding to this solution.

        """
        logger.info(logging_preamble + "MATCH PRESSURE PROBLEM")
        logger.info(logging_preamble + f"{pressure_target.describe()} ->")
        min_vol, max_vol = self.get_chamber_volume_limits(
            pressure_target=pressure_target, acc=acc, logging_preamble=logging_preamble + "\t"
        )

        valid_range_prompt = (
            f"valid range of chamber_volume: [{min_vol * 1e3:.3f} L, {max_vol * 1e3:.3f} L]"
        )
        if chamber_volume < min_vol:
            raise ValueError(
                "specified chamber not enough to prevent miniimum bomb state free fraction constraint violation.\n"
                + valid_range_prompt
            )
        elif chamber_volume > max_vol:
            raise ValueError(
                "specified chamber volume too large for the targeted pressure to develop.\n"
                + valid_range_prompt
            )

        gun = self.solve_reduced_burn_rate_at_pressure(
            charge_mass=self.charge_mass,
            chamber_volume=chamber_volume,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
        )
        logger.info(logging_preamble + "END")
        return gun

    def solve_chamber_volume_at_velocity_and_pressure(
        self,
        *,
        pressure_target: PressureTarget,
        velocity_target: float,
        n_intg: int,
        acc: float,
        logging_preamble: str = "",
    ) -> Gun:
        logger.info(logging_preamble + "MATCH VELOCITY AND PRESSURE PROBLEM")
        logger.info(
            logging_preamble
            + f"velocity of {velocity_target:.1f} m/s, {pressure_target.describe()} ->"
        )
        min_vol, max_vol = self.get_chamber_volume_limits(
            pressure_target=pressure_target, acc=acc, logging_preamble=logging_preamble + "\t"
        )

        def f(chamber_volume: float) -> float:
            logger.info(chamber_volume)
            gun = self.solve_reduced_burn_rate_at_pressure(
                charge_mass=self.charge_mass,
                chamber_volume=chamber_volume,
                pressure_target=pressure_target,
                n_intg=n_intg,
                acc=acc,
                logging_preamble=logging_preamble,
            )
            states = gun.to_travel(travel=self.travel, n_intg=n_intg, acc=acc)
            logger.info(states.tabulate())
            muzzle_state = states.get_state_by_marker(significance=Significance.MUZZLE)

            return muzzle_state.velocity - velocity_target

        dv_max = f(chamber_volume=min_vol)
        dv_min = f(chamber_volume=max_vol)
        logger.info(logging_preamble + "VELOCITY RANGE")
        logger.info(
            logging_preamble
            + f"-> velocity from {velocity_target + dv_min:.3f} to {velocity_target + dv_max:.3f} m/s"
        )
        if not dv_min < 0 < dv_max:
            raise ValueError(
                "targeted velocity is not achievable in the range of valid loading condition."
            )

        # target velocity is achievable, find the corresponding charge mass to get it.
        chamber_volume, _ = dekker(f=f, x_0=min_vol, x_1=max_vol, tol=acc)
        gun = self.solve_reduced_burn_rate_at_pressure(
            charge_mass=self.charge_mass,
            chamber_volume=chamber_volume,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
        )

        logger.info(
            logging_preamble
            + f"-> chamber volume {chamber_volume * 1e3:.3f} L, r.b.r {gun.charge.reduced_burnrate:.2e} s^-1"
        )
        logger.info(logging_preamble + "END")
        return gun
