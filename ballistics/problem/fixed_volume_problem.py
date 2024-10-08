from __future__ import annotations

import logging
from typing import Tuple

from attrs import frozen

from .. import MINIMUM_BOMB_STATE_FREE_FRACTION, Significance
from ..gun import Gun
from ..num import dekker
from .base_problem import BaseProblem
from .pressure_target import PressureTarget

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class FixedVolumeProblem(BaseProblem):
    """
    Given known gun and charge loading parameters, deduce the charge that is required to *match*
    the performance, in terms of peak pressure and shot velocity.
    """

    chamber_volume: float

    def get_gun(self, *, reduced_burnrate: float, charge_mass: float, **kwargs) -> Gun:
        return super().get_gun(
            reduced_burnrate=reduced_burnrate,
            charge_mass=charge_mass,
            chamber_volume=self.chamber_volume,
        )

    def get_charge_mass_limits(
        self, *, pressure_target: PressureTarget, acc: float, logging_preamble: str = ""
    ) -> Tuple[float, float]:
        """
        Find the maximum and minimum valid charge mass value for the outlined gun design

        Parameters
        ----------
        pressure_target, acc: `ballistics.problem.pressure_target.PressureTarget`, float
            see `FixedVolumeProblem.solve_reduced_burn_rate` for more information.

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
        logger.info(logging_preamble + "CHARGE LIMIT")
        logger.info(logging_preamble + f"{pressure_target.describe()} ->")

        def f_ff(charge_mass: float) -> float:
            test_gun = self.get_gun(reduced_burnrate=1, charge_mass=charge_mass)
            return test_gun.bomb_free_fraction - MINIMUM_BOMB_STATE_FREE_FRACTION

        chamber_fill_mass = self.chamber_volume * self.propellant.density

        upper_limit = min(dekker(f_ff, 0, chamber_fill_mass, tol=chamber_fill_mass * acc))

        def f_p(charge_mass: float) -> float:
            # note this is defined on [0, chamber_fill_mass]
            test_gun = self.get_gun(reduced_burnrate=1, charge_mass=charge_mass)
            test_gun_bomb_pressure = pressure_target.retrieve_from(test_gun.get_bomb_state())
            return test_gun_bomb_pressure - pressure_target.value

        lower_limit = max(dekker(f_p, 0, upper_limit, tol=chamber_fill_mass * acc))

        logger.info(
            logging_preamble + f"-> charge from {lower_limit:.3f} kg to {upper_limit:.3f} kg"
        )
        logger.info(logging_preamble + "END")
        return lower_limit, upper_limit

    def solve_reduced_burn_rate_for_charge_at_pressure(
        self,
        *,
        charge_mass: float,
        pressure_target: PressureTarget,
        n_intg: int,
        acc: float,
        logging_preamble: str = "",
        **kwargs,
    ) -> Gun:
        """
        solves the reduced burn rate such that the peak pressure developed in bore
        matches the desired value. This is the outer, user facing function that validates
        the input by checking against the calcualted charge mass limits. Implementation
        instead under `BaseProblem.solve_reduced_burn_rate_at_pressure` method.

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

        gun = self.solve_reduced_burn_rate_at_pressure(
            charge_mass=charge_mass,
            chamber_volume=self.chamber_volume,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
        )
        logger.info(logging_preamble + "END")

        return gun

    def solve_charge_mass_at_velocity_and_pressure(
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
        min_mass, max_mass = self.get_charge_mass_limits(
            pressure_target=pressure_target, acc=acc, logging_preamble=logging_preamble + "\t"
        )

        def f(charge_mass: float) -> float:
            gun = self.solve_reduced_burn_rate_at_pressure(
                charge_mass=charge_mass,
                chamber_volume=self.chamber_volume,
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
            + f"-> velocity from {velocity_target + dv_min:.3f} to {velocity_target + dv_max:.3f} m/s"
        )
        if not dv_min < 0 < dv_max:
            raise ValueError(
                "targeted velocity is not achievable in the range of valid loading condition."
            )

        # target velocity is achievable, find the corresponding charge mass to get it.
        charge_mass, _ = dekker(f=f, x_0=min_mass, x_1=max_mass, tol=acc)
        gun = self.solve_reduced_burn_rate_at_pressure(
            charge_mass=charge_mass,
            chamber_volume=self.chamber_volume,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
        )

        logger.info(
            logging_preamble
            + f"-> charge mass {charge_mass:.3f} kg, r.b.r {gun.charge.reduced_burnrate:.2e} s^-1"
        )
        logger.info(logging_preamble + "END")
        return gun
