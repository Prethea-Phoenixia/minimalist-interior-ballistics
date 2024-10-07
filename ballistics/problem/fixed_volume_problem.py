from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, Tuple

from .. import (DEFAULT_GUN_START_PRESSURE, DFEAULT_GUN_LOSS_FRACTION,
                MINIMUM_BOMB_STATE_FREE_FRACTION,
                REDUCED_BURN_RATE_INITIAL_GUESS, Significance)
from ..charge import Charge, Propellant
from ..gun import Gun
from ..num import dekker
from .pressure_target import PressureTarget

if TYPE_CHECKING:
    from ..form_function import FormFunction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FixedVolumeProblem:
    """
    Given known gun and charge loading parameters, deduce the charge that is required to *match*
    the performance, in terms of peak pressure and shot velocity.
    """

    propellant: Propellant
    form_function: FormFunction

    cross_section: float
    shot_mass: float
    chamber_volume: float
    travel: float
    loss_fraction: float = DFEAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE

    def get_test_gun(self, reduced_burnrate: float, charge_mass: float) -> Gun:
        charge = Charge.from_propellant(
            reduced_burnrate=reduced_burnrate,
            propellant=self.propellant,
            form_function=self.form_function,
        )

        gun = Gun(
            cross_section=self.cross_section,
            shot_mass=self.shot_mass,
            charge_mass=charge_mass,
            charge=charge,
            chamber_volume=self.chamber_volume,
            loss_fraction=self.loss_fraction,
            start_pressure=self.start_pressure,
        )
        return gun

    def get_charge_mass_limits(
        self, pressure_target: PressureTarget, acc: float, logging_preamble: str = ""
    ) -> Tuple[float, float]:
        """
        Find the maximum and minimum valid charge mass value for the outlined gun design

        Parameters
        ----------
        pressure, target, acc: float, Target, float
            see `FixedVolumeProblem.solve_reduced_burn_rate` for more information.

        Raises
        ------
        ValueError
            in case existing charge is

        Returns
        -------
        lower_limit, upper_limit: float

        Notes
        -----
        The bomb-pressure refers to the pressure developed in a gun as its charges
        have completelly burnt, before the projectile has moved. This corresponds
        to the case where the reduced burn-rate is infinitesimally high. It has the
        convenient property that it is the maximum pressure that can be developed with
        a certain charge loading.

        The lower limit is found by finding the required mass of charge to bring the
        gun's bomb-pressure to at least the targeted pressure levels.

        The upper limit is found when the complete combustion of charge within
        chamber reduces volumetric free fraction to less than specified in module wide
        constant `ballistics.MINIMUM_BOMB_STATE_FREE_FRACTION`, since the Nobel-Abel
        equation of state does not model high pressure (and correspondingly
        high incompressibility) well.

        The reduced-burn rate that corresponds to the limiting charge
        weights asymptotically approaches `+inf` for the lower limit, and 0 for the
        upper limit. Care is taken such that the returned limits, being numerically
        solved, errs on the conservative side.
        """

        def f_ff(charge_mass: float) -> float:
            test_gun = self.get_test_gun(reduced_burnrate=1, charge_mass=charge_mass)
            return test_gun.bomb_free_fraction - MINIMUM_BOMB_STATE_FREE_FRACTION

        chamber_fill_mass = self.chamber_volume * self.propellant.density

        upper_limit = min(dekker(f_ff, 0, chamber_fill_mass, tol=chamber_fill_mass * acc))

        def f_p(charge_mass: float) -> float:
            # note this is defined on [0, chamber_fill_mass]
            test_gun = self.get_test_gun(reduced_burnrate=1, charge_mass=charge_mass)
            test_gun_bomb_pressure = pressure_target.retrieve_from(test_gun.get_bomb_state())
            return test_gun_bomb_pressure - pressure_target.value

        lower_limit = max(dekker(f_p, 0, upper_limit, tol=chamber_fill_mass * acc))

        logger.info(logging_preamble + "CHARGE LIMIT")
        logger.info(logging_preamble + f"{pressure_target.describe()} ->")
        logger.info(
            logging_preamble + f"-> charge from {lower_limit:.2f} kg to {upper_limit:.2f} kg"
        )
        logger.info(logging_preamble + "END")
        return lower_limit, upper_limit

    def solve_reduced_burn_rate_at_pressure(
        self,
        charge_mass: float,
        pressure_target: PressureTarget,
        n_intg: int,
        acc: float,
        logging_preamble: str = "",
    ) -> Gun:
        """
        solves the reduced burn rate such that the peak pressure developed in bore
        matches the desired value. This is the outer, user facing function that validates
        the input by checking against the known charge mass limits. The calculation is
        instead under `FixedVolumeProblem._solve_reduced_burn_rate_at_pressure` method.

        Parameters
        ----------
        charge_mass: float
            the mass of the charge.
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
        min_mass, max_mass = self.get_charge_mass_limits(
            pressure_target=pressure_target, acc=acc, logging_preamble=logging_preamble + "\t"
        )

        valid_range_prompt = f"valid range of charge mass: [{min_mass:.3f}, {max_mass:.3f}]"
        if charge_mass < min_mass:
            raise ValueError(
                "specified charge cannot possibly develop the targeted pressure.\n"
                + valid_range_prompt
            )
        elif charge_mass > max_mass:
            raise ValueError(
                "specified charge exceed maximum load density considered.\n" + valid_range_prompt
            )

        gun = self._solve_reduced_burn_rate_at_pressure(
            charge_mass=charge_mass, pressure_target=pressure_target, n_intg=n_intg, acc=acc
        )

        logger.info(logging_preamble + "END")

        return gun

    def _solve_reduced_burn_rate_at_pressure(
        self,
        charge_mass: float,
        pressure_target: PressureTarget,
        n_intg: int,
        acc: float,
        logging_preamble: str = "",
    ) -> Gun:

        def f(reduced_burnrate: float) -> float:
            test_gun = self.get_test_gun(reduced_burnrate=reduced_burnrate, charge_mass=charge_mass)
            states = test_gun.to_burnout(n_intg=n_intg, acc=acc, abort_travel=self.travel)
            delta_p = (
                pressure_target.retrieve_from(
                    states.get_state_by_marker(Significance.PEAK_PRESSURE)
                )
                - pressure_target.value
            )
            return delta_p

        # solve the burn rate coefficient on (0, +inf)

        """
        first, find two estimate, est and est' (rendered as est_prime) such that
        the solution is bracketed
        """
        est = est_prime = REDUCED_BURN_RATE_INITIAL_GUESS
        f_est = f_est_prime = f(est)
        while f_est * f_est_prime >= 0:
            if f_est > 0:  # burnt too fast
                est, est_prime = est / 10, est  # reduce rbr by 1 oom
            elif f_est == 0:  # this is *exceedingly* unlikely to happen but still.
                est, est_prime = est / 10, est * 10
            else:
                est, est_prime = est * 10, est
            f_est, f_est_prime = f(est), f_est

        """
        then, use `ballistics.num.dekker` to find the exact solution. this is necessary
        since the accuracy specification is realtive and the order of magnitude of the
        estimates aren't known a-priori
        """
        while abs(est - est_prime) > acc * min(est, est_prime):
            est, est_prime = dekker(f=f, x_0=est, x_1=est_prime, tol=min(est, est_prime) * acc)

        logger.info(logging_preamble + f"charge {charge_mass:.2f} kg -> r.b.r {est:.2e} s^-1")

        return self.get_test_gun(reduced_burnrate=est, charge_mass=charge_mass)

    def solve_charge_mass_at_velocity_and_pressure(
        self,
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
        min_mass, max_mass = self.get_charge_mass_limits(
            pressure_target=pressure_target, acc=acc, logging_preamble=logging_preamble + "\t"
        )

        def f(charge_mass: float) -> float:
            gun = self._solve_reduced_burn_rate_at_pressure(
                charge_mass=charge_mass,
                pressure_target=pressure_target,
                n_intg=n_intg,
                acc=acc,
                logging_preamble=logging_preamble,
            )
            states = gun.to_travel(travel=self.travel, n_intg=n_intg, acc=acc)
            muzzle_state = states.get_state_by_marker(significance=Significance.MUZZLE)

            return muzzle_state.velocity - velocity_target

        dv_min = f(charge_mass=min_mass)
        dv_max = f(charge_mass=max_mass)
        logger.info(logging_preamble + "VELOCITY RANGE")
        logger.info(
            logging_preamble
            + f"-> velocity from {velocity_target + dv_min:.2f} to {velocity_target + dv_max:.2f} m/s"
        )
        if not dv_min < 0 < dv_max:
            raise ValueError(
                "targeted velocity is not achievable in the range of valid loading condition."
            )

        # target velocity is achievable, find the corresponding charge mass to get it.
        charge_mass, _ = dekker(f=f, x_0=min_mass, x_1=max_mass, tol=acc)
        gun = self._solve_reduced_burn_rate_at_pressure(
            charge_mass=charge_mass, pressure_target=pressure_target, n_intg=n_intg, acc=acc
        )

        logger.info(
            logging_preamble
            + f"-> charge mass {charge_mass:.2f} kg, r.b.r {gun.charge.reduced_burnrate:.2e} s^-1"
        )
        logger.info(logging_preamble + "END")
        return gun
