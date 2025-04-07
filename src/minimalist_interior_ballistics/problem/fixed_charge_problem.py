from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Tuple, override

from attrs import frozen, asdict

from .. import Significance
from ..gun import Gun
from ..num import dekker, gss_max
from .base_problem import BaseProblem, accepts_reduced_burnrate, accepts_charge_mass
from .pressure_target import PressureTarget

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # these are required for pdoc to locate the references
    from ..charge import Propellant
    from ..form_function import FormFunction


@frozen(kw_only=True)
class FixedChargeProblem(BaseProblem):
    charge_mass: Optional[float] = None
    charge_masses: list[float] | tuple[float, ...] = tuple()

    @classmethod
    def from_base_problem(
        cls,
        base_problem: BaseProblem,
        charge_mass: Optional[float] = None,
        charge_masses: list[float] | tuple[float, ...] = tuple(),
    ) -> FixedChargeProblem:
        return cls(**asdict(base_problem, recurse=False), charge_mass=charge_mass, charge_masses=charge_masses)

    @accepts_reduced_burnrate
    def get_gun(self, chamber_volume: float, reduced_burnrates: tuple[float, ...], **kwargs) -> Gun:
        return super(FixedChargeProblem, self).get_gun(
            charge_mass=self.charge_mass,
            charge_masses=self.charge_masses,
            chamber_volume=chamber_volume,
            reduced_burnrates=reduced_burnrates,
        )

    @accepts_charge_mass
    def get_chamber_min_volume(self, charge_masses: tuple[float, ...]) -> float:
        return sum(charge_mass / propellant.density for charge_mass, propellant in zip(charge_masses, self.propellants))

    @cached_property
    def chamber_min_volume(self) -> float:
        return self.get_chamber_min_volume(charge_mass=self.charge_mass, charge_masses=self.charge_masses)

    def get_gun_at_pressure(
        self,
        pressure_target: PressureTarget,
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
        *,
        chamber_volume: float,
        **kwargs,
    ) -> Gun:
        return super(FixedChargeProblem, self).get_gun_at_pressure(
            pressure_target=pressure_target,
            chamber_volume=chamber_volume,
            charge_mass=self.charge_mass,
            charge_masses=self.charge_masses,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
        )

    def get_chamber_volume_limits(self, pressure_target: PressureTarget) -> Tuple[float, float]:
        """
        find the range of valid chamber volume

        Parameters
        ----------
        pressure_target: `minimalist_interior_ballistics.problem.pressure_target.PressureTarget`
            see `minimalist_interior_ballistics.problem.base_problem.BaseProblem.get_gun_at_pressure`
            for more information.

        Returns
        -------
        lower_limit, upper_limit: float

        Notes
        -----
        For more explanation of the rationale, reference
        `minimalist_interior_ballistics.problem.fixed_volume_problem.FixedVolumeProblem.get_charge_mass_limits`.

        """
        logger.info("get chamber volume limits")

        def f_ff(chamber_volume: float) -> float:
            test_gun = self.get_gun(
                chamber_volume=chamber_volume, reduced_burnrates=tuple(1.0 for _ in self.propellants)
            )
            return test_gun.bomb_free_fraction - self.acc

        chamber_min_volume = self.chamber_min_volume

        bound = chamber_min_volume
        while f_ff(bound) <= 0:
            bound *= 2

        lower_limit = max(dekker(f=f_ff, x_0=chamber_min_volume, x_1=bound, tol=chamber_min_volume * self.acc))

        safe_target = pressure_target * (1 + self.acc)

        def f_p(chamber_volume: float) -> float:
            test_gun = self.get_gun(
                chamber_volume=chamber_volume, reduced_burnrates=tuple(1.0 for _ in self.propellants)
            )
            return safe_target.get_difference(test_gun.get_bomb_state())

        while f_p(bound) >= 0:
            bound *= 2

        upper_limit = min(dekker(f=f_p, x_0=lower_limit, x_1=bound, tol=chamber_min_volume * self.acc))

        logger.info(
            f"chamber volume limit for {pressure_target.describe()} solved to be "
            + f"{lower_limit * 1e3:.3f} L to {upper_limit * 1e3:.3f} L"
        )
        return lower_limit, upper_limit

    def solve_reduced_burn_rate_for_volume_at_pressure(
        self,
        chamber_volume: float,
        pressure_target: PressureTarget,
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
    ) -> Gun:
        """
        solves the reduced burn rate such that the peak pressure developed in bore
        matches the desired value. This is the outer, user facing function that validates
        the input by checking against the calculated chamber volume limits. Implementation
        is instead under `minimalist_interior_ballistics.problem.base_problem.BaseProblem.get_gun_at_pressure`
        method.

        Parameters
        ----------
        reduced_burnrate_ratios: list[float] | tuple[float, ...]
            if more than one charge is specified, then the ratio between the reduced burnrates of each is
            required.
        chamber_volume: float
            volume of the chamber.
        pressure_target: float, `minimalist_interior_ballistics.problem.pressure_target.PressureTarget`
            the pressure to target, along with its point-of-measurement.

        Raises
        ------
        ValueError
            if the specified charge mass is either too low or too high for this
            gun design.

        Returns
        -------
        gun: `minimalist_interior_ballistics.gun.MonoChargeGun` object
            the gun corresponding to this solution.

        """

        logger.info(f"solve reduced burn rate for {pressure_target.describe()}")
        min_vol, max_vol = self.get_chamber_volume_limits(pressure_target=pressure_target)

        valid_range_prompt = f"valid range of chamber_volume: [{min_vol * 1e3:.3f} L, {max_vol * 1e3:.3f} L]"
        if chamber_volume < min_vol:
            raise ValueError(
                "specified chamber volume too small to accomodate charge incompressibility at bomb state.\n"
                + valid_range_prompt
            )
        elif chamber_volume > max_vol:
            raise ValueError(
                "specified chamber volume too large for the targeted pressure to develop.\n" + valid_range_prompt
            )

        gun = self.get_gun_at_pressure(
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            chamber_volume=chamber_volume,
            pressure_target=pressure_target,
        )
        logger.info(
            "reduced burn rates solved to " + ", ".join(f"{charge.reduced_burnrate:.2e} s^-1" for charge in gun.charges)
        )
        return gun

    def get_limiting_guns_at_pressure(
        self,
        pressure_target: PressureTarget,
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
    ) -> tuple[Gun, Gun, Gun]:

        logger.info("getting limiting cases for" + f" {pressure_target.describe()}")

        vol_min, vol_max = self.get_chamber_volume_limits(pressure_target=pressure_target)

        def get_gun_with_volume(chamber_volume: float) -> Gun:
            return self.get_gun_at_pressure(
                reduced_burnrate_ratios=reduced_burnrate_ratios,
                chamber_volume=chamber_volume,
                pressure_target=pressure_target,
            )

        def f(chamber_volume: float) -> float:
            gun = get_gun_with_volume(chamber_volume=chamber_volume)
            states = gun.to_travel(travel=self.travel, n_intg=self.n_intg, acc=self.acc)
            muzzle_state = states.get_state_by_marker(significance=Significance.MUZZLE)

            return muzzle_state.velocity

        vol_opt = sum(gss_max(f, x_0=vol_min, x_1=vol_max, tol=self.chamber_min_volume * self.acc)) * 0.5

        results = (
            get_gun_with_volume(chamber_volume=vol_min),
            get_gun_with_volume(chamber_volume=vol_opt),
            get_gun_with_volume(chamber_volume=vol_max),
        )

        logger.info(f"optimal chamber volume {vol_opt * 1e3:.3f} L")

        return results

    def solve_chamber_volume_at_pressure_for_velocity(
        self,
        pressure_target: PressureTarget,
        velocity_target: float,
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
    ) -> Tuple[Optional[Gun], Optional[Gun]]:

        logger.info(f"solve chamber volume for {velocity_target:.1f} m/s and {pressure_target.describe()}")

        gun_vol_min, gun_opt, gun_vol_max = self.get_limiting_guns_at_pressure(
            pressure_target=pressure_target, reduced_burnrate_ratios=reduced_burnrate_ratios
        )

        def get_mv(gun: Gun) -> float:
            return gun.to_travel(n_intg=self.n_intg, acc=self.acc).muzzle_velocity

        v_vol_min = get_mv(gun_vol_min)
        v_vol_max = get_mv(gun_vol_max)
        v_opt = get_mv(gun_opt)

        v_min = min(v_vol_min, v_vol_max)
        logger.info(f"velocity from {v_min:.3f} and {v_opt:.3f} m/s")

        vol_min = gun_vol_min.chamber_volume
        vol_max = gun_vol_max.chamber_volume
        vol_opt = gun_opt.chamber_volume

        def f(chamber_volume: float) -> Gun:
            return self.get_gun_at_pressure(
                reduced_burnrate_ratios=reduced_burnrate_ratios,
                chamber_volume=chamber_volume,
                pressure_target=pressure_target,
            )

        def g(vol_i: float, vol_j: float, v_i: float, v_j: float) -> Optional[Gun]:
            if min(v_i, v_j) <= velocity_target <= max(v_i, v_j):
                # target velocity is achievable, find the corresponding charge mass to get it.
                chamber_volume, _ = dekker(
                    f=lambda x: get_mv(f(x)) - velocity_target,
                    x_0=vol_i,
                    x_1=vol_j,
                    tol=self.acc * self.chamber_min_volume,
                )
                gun = f(chamber_volume=chamber_volume)
                return gun
            else:
                return None

        results = (
            g(vol_i=vol_min, vol_j=vol_opt, v_i=v_vol_min, v_j=v_opt),
            g(vol_i=vol_opt, vol_j=vol_max, v_i=v_opt, v_j=v_vol_max),
        )

        logger.info(
            "low chamber volume "
            + (f"{results[0].chamber_volume*1e3:.1f} L " if results[0] else "impossible ")
            + "high chamber volume "
            + (f"{results[1].chamber_volume*1e3:.1f} L " if results[1] else "impossible ")
        )

        return results
