from __future__ import annotations

import logging
from functools import cached_property
from typing import Optional, Tuple

from attrs import frozen

from .. import DEFAULT_ACC, DEFAULT_STEPS, Significance
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
        self,
        pressure_target: PressureTarget,
        *,
        acc: float = DEFAULT_ACC,
        logging_preamble: str = "",
    ) -> Tuple[float, float]:
        """
        find the range of valid chamber volume

        Parameters
        ----------
        pressure_target, acc: `ballistics.problem.pressure_target.PressureTarget`, float
            see `ballistics.problem.base_problem.BaseProblem.get_gun_developing_pressure`
            for more information.

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
        `ballistics.problem.fixed_volume_problem.FixedVolumeProblem.get_charge_mass_limits`.

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
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        logging_preamble: str = "",
        **kwargs,
    ) -> Gun:
        """
        solves the reduced burn rate such that the peak pressure developed in bore
        matches the desired value. This is the outer, user facing function that validates
        the input by checking against the calculated chamber volume limits. Implementation
        is instead under `ballistics.problem.base_problem.BaseProblem.get_gun_developing_pressure`
        method.

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
            pressure_target=pressure_target,
            acc=acc,
            logging_preamble=logging_preamble + "\t",
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

    def solve_chamber_volume_at_pressure_for_velocity(
        self,
        pressure_target: PressureTarget,
        *,
        velocity_target: Optional[float] = None,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        logging_preamble: str = "",
    ) -> Tuple[Optional[Gun], Optional[Gun], Optional[Gun]]:
        logger.info(
            logging_preamble
            + "MATCH VELOCITY AND PRESSURE PROBLEM "
            + f"{velocity_target:.1f} m/s, {pressure_target.describe()} ->"
        )
        vol_min, vol_max = self.get_chamber_volume_limits(
            pressure_target=pressure_target,
            acc=acc,
            logging_preamble=logging_preamble + "\t",
        )

        def get_gun_with_volume(chamber_volume: float) -> Gun:
            return self.get_gun_developing_pressure(
                charge_mass=self.charge_mass,
                chamber_volume=chamber_volume,
                pressure_target=pressure_target,
                n_intg=n_intg,
                acc=acc,
                logging_preamble=logging_preamble + "\t",
            )

        def f(chamber_volume: float) -> float:
            gun = get_gun_with_volume(chamber_volume=chamber_volume)
            states = gun.to_travel(
                travel=self.travel,
                n_intg=n_intg,
                acc=acc,
                logging_preamble=logging_preamble + "\t",
            )
            muzzle_state = states.get_state_by_marker(significance=Significance.MUZZLE)

            return muzzle_state.velocity

        vol_opt = sum(gss_max(f, x_0=vol_min, x_1=vol_max, tol=self.chamber_min_volume * acc)) * 0.5
        v_opt = f(vol_opt)

        v_min_vol = f(chamber_volume=vol_min)
        v_max_vol = f(chamber_volume=vol_max)

        v_min = min(v_min_vol, v_max_vol)

        logger.info(logging_preamble + f"-> VELOCITY RANGE {v_min:.3f} TO {v_opt:.3f} m/s")

        if velocity_target:
            if not v_min < velocity_target <= v_opt:
                raise ValueError(
                    "targeted velocity is not achievable in the range of valid loading condition."
                )

            def g(vol_i: float, vol_j: float, v_i: float, v_j: float) -> Optional[Gun]:
                if min(v_i, v_j) <= velocity_target <= max(v_i, v_j):
                    # target velocity is achievable, find the corresponding charge mass to get it.
                    chamber_volume, _ = dekker(
                        f=lambda x: f(x) - velocity_target,
                        x_0=vol_i,
                        x_1=vol_j,
                        tol=acc * self.chamber_min_volume,
                    )
                    gun = get_gun_with_volume(chamber_volume=chamber_volume)

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
                g(vol_i=vol_min, vol_j=vol_opt, v_i=v_min_vol, v_j=v_opt),
                None,
                g(vol_i=vol_opt, vol_j=vol_max, v_i=v_opt, v_j=v_max_vol),
            )
        else:
            return (
                get_gun_with_volume(chamber_volume=vol_min),
                get_gun_with_volume(chamber_volume=vol_opt),
                get_gun_with_volume(chamber_volume=vol_max),
            )