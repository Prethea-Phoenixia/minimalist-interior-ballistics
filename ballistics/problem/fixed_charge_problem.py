from __future__ import annotations

import logging
from functools import cached_property
from typing import Optional, Tuple

from attrs import frozen

from .. import Significance
from ..gun import Gun
from ..num import dekker, gss_max
from .base_problem import BaseProblem
from .pressure_target import PressureTarget

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class FixedChargeProblem(BaseProblem):
    charge_mass: float

    def get_gun(self, *, chamber_volume: float, reduced_burnrate: float = 0, **kwargs) -> Gun:
        return super().get_gun(
            charge_mass=self.charge_mass,
            chamber_volume=chamber_volume,
            reduced_burnrate=reduced_burnrate,
        )

    @cached_property
    def chamber_min_volume(self) -> float:
        return self.charge_mass / self.propellant.density

    def get_chamber_volume_limits(
        self, pressure_target: PressureTarget, *, acc: float, logging_preamble: str = ""
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

        def f_ff(chamber_volume: float) -> float:
            test_gun = self.get_gun(chamber_volume=chamber_volume)
            return test_gun.bomb_free_fraction - acc

        chamber_min_volume = self.chamber_min_volume

        bound = chamber_min_volume
        while f_ff(bound) < 0:
            bound *= 2

        lower_limit = max(
            dekker(f=f_ff, x_0=chamber_min_volume, x_1=bound, tol=chamber_min_volume * acc)
        )

        def f_p(chamber_volume: float) -> float:
            test_gun = self.get_gun(chamber_volume=chamber_volume)
            test_gun_bomb_pressure = pressure_target.retrieve_from(test_gun.get_bomb_state())
            return test_gun_bomb_pressure - pressure_target.value

        bound = lower_limit
        while f_p(bound) > 0:
            bound *= 2

        upper_limit = min(dekker(f=f_p, x_0=lower_limit, x_1=bound, tol=chamber_min_volume * acc))

        logger.info(
            logging_preamble
            + f"VOLUME LIMIT {pressure_target.describe()} "
            + f"-> {lower_limit * 1e3:.3f} L TO {upper_limit * 1e3:.3f} L END"
        )
        return lower_limit, upper_limit

    def solve_reduced_burn_rate_for_volume_at_pressure(
        self,
        chamber_volume: float,
        pressure_target: PressureTarget,
        *,
        n_intg: int,
        acc: float,
        logging_preamble: str = "",
        **kwargs,
    ) -> Gun:
        """
        solves the reduced burn rate such that the peak pressure developed in bore
        matches the desired value. This is the outer, user facing function that validates
        the input by checking against the calculated chamber volume limits. Implementation
        is instead under `BaseProblem.get_gun_developing_pressure` method.

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
        logger.info(
            logging_preamble + "MATCH PRESSURE PROBLEM " + f"{pressure_target.describe()} ->"
        )
        min_vol, max_vol = self.get_chamber_volume_limits(
            pressure_target=pressure_target, acc=acc, logging_preamble=logging_preamble + "\t"
        )

        valid_range_prompt = (
            f"valid range of chamber_volume: [{min_vol * 1e3:.3f} L, {max_vol * 1e3:.3f} L]"
        )
        if chamber_volume < min_vol:
            raise ValueError(
                "specified chamber volume too small to accomodate charge incompressibility"
                + " at bomb state.\n"
                + valid_range_prompt
            )
        elif chamber_volume > max_vol:
            raise ValueError(
                "specified chamber volume too large for the targeted pressure to develop.\n"
                + valid_range_prompt
            )

        gun = self.get_gun_developing_pressure(
            charge_mass=self.charge_mass,
            chamber_volume=chamber_volume,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
            logging_preamble=logging_preamble + "\t",
        )
        logger.info(
            logging_preamble + f"-> REDUCED BURN RATE {gun.charge.reduced_burnrate:.2e} s^-1 END"
        )
        return gun

    def solve_chamber_volume_at_velocity_and_pressure(
        self,
        velocity_target: float,
        pressure_target: PressureTarget,
        *,
        n_intg: int,
        acc: float,
        logging_preamble: str = "",
    ) -> Tuple[Optional[Gun], Optional[Gun]]:
        logger.info(
            logging_preamble
            + "MATCH VELOCITY AND PRESSURE PROBLEM "
            + f"{velocity_target:.1f} m/s, {pressure_target.describe()} ->"
        )
        vol_min, vol_max = self.get_chamber_volume_limits(
            pressure_target=pressure_target, acc=acc, logging_preamble=logging_preamble + "\t"
        )

        def f(chamber_volume: float) -> float:
            gun = self.get_gun_developing_pressure(
                charge_mass=self.charge_mass,
                chamber_volume=chamber_volume,
                pressure_target=pressure_target,
                n_intg=n_intg,
                acc=acc,
                logging_preamble=logging_preamble + "\t",
            )
            states = gun.to_travel(
                travel=self.travel,
                n_intg=n_intg,
                acc=acc,
                logging_preamble=logging_preamble + "\t",
            )
            # logger.info(states.tabulate())
            muzzle_state = states.get_state_by_marker(significance=Significance.MUZZLE)

            return muzzle_state.velocity - velocity_target

        vol_opt = sum(gss_max(f, x_0=vol_min, x_1=vol_max, tol=self.chamber_min_volume * acc)) * 0.5
        dv_opt = f(vol_opt)

        dv_min_vol = f(chamber_volume=vol_min)
        dv_max_vol = f(chamber_volume=vol_max)

        dv_min = min(dv_min_vol, dv_max_vol)

        logger.info(
            logging_preamble
            + f"-> VELOCITY RANGE {velocity_target + dv_min:.3f} "
            + f"TO {velocity_target + dv_opt:.3f} m/s"
        )
        if not dv_min < 0 < dv_opt:
            raise ValueError(
                "targeted velocity is not achievable in the range of valid loading condition."
            )

        def g(vol_i: float, vol_j: float, dv_i: float, dv_j: float) -> Optional[Gun]:
            if min(dv_i, dv_j) <= 0 <= max(dv_i, dv_j):
                # target velocity is achievable, find the corresponding charge mass to get it.
                chamber_volume, _ = dekker(
                    f=f, x_0=vol_i, x_1=vol_j, tol=acc * self.chamber_min_volume
                )
                gun = self.get_gun_developing_pressure(
                    charge_mass=self.charge_mass,
                    chamber_volume=chamber_volume,
                    pressure_target=pressure_target,
                    n_intg=n_intg,
                    acc=acc,
                    logging_preamble=logging_preamble + "\t",
                )

                logger.info(
                    logging_preamble
                    + f"-> CHAMBER {chamber_volume * 1e3:.3f} L, "
                    + f"REDUCED BURN RATE {gun.charge.reduced_burnrate:.2e} s^-1"
                )
                return gun
            else:
                return None

        logger.info(logging_preamble + "END")

        return (
            g(vol_i=vol_min, vol_j=vol_opt, dv_i=dv_min_vol, dv_j=dv_opt),
            g(vol_i=vol_opt, vol_j=vol_max, dv_i=dv_opt, dv_j=dv_max_vol),
        )
