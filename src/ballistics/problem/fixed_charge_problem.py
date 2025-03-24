from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Tuple

from attrs import frozen

from .. import DEFAULT_ACC, DEFAULT_STEPS, Significance
from ..gun import Gun
from ..num import dekker, gss_max
from .base_problem import BaseProblem
from .pressure_target import PressureTarget

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class FixedChargeProblem(BaseProblem):

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

    @classmethod
    def from_base_problem(
        cls,
        base_problem: BaseProblem,
        charge_mass: Optional[float] = None,
        charge_masses: list[float] | tuple[float, ...] = tuple(),
    ) -> FixedChargeProblem:
        return cls(
            name=base_problem.name,
            description=base_problem.description,
            family=base_problem.family,
            propellant=base_problem.propellant,
            propellants=base_problem.propellants,
            form_function=base_problem.form_function,
            form_functions=base_problem.form_functions,
            cross_section=base_problem.cross_section,
            shot_mass=base_problem.shot_mass,
            travel=base_problem.travel,
            loss_fraction=base_problem.loss_fraction,
            start_pressure=base_problem.start_pressure,
            charge_mass=charge_mass,
            charge_masses=charge_masses,
        )

    def get_gun(
        self,
        *,
        chamber_volume: float,
        reduced_burnrate: Optional[float] = None,
        reduced_burnrates: Optional[tuple[float, ...] | list[float]] = None,
        **kwargs,
    ) -> Gun:

        if reduced_burnrate:
            reduced_burnrates = tuple([reduced_burnrate])

        if reduced_burnrates:
            if len(self.charge_masses) != len(reduced_burnrates):
                raise ValueError(
                    "reduced_burnrates must have the same dimension as self.propellants, charge_masses, and form_functions"
                )
        else:
            raise ValueError("invalid parameters.")

        return super().get_gun(
            charge_masses=self.charge_masses, chamber_volume=chamber_volume, reduced_burnrates=reduced_burnrates
        )

    @cached_property
    def chamber_min_volume(self) -> float:
        return sum(
            charge_mass / propellant.density for charge_mass, propellant in zip(self.charge_masses, self.propellants)
        )
        # return self.charge_mass / self.propellant.density

    def get_chamber_volume_limits(
        self, pressure_target: PressureTarget, acc: float = DEFAULT_ACC
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
        logger.info("get chamber volume limits")

        def f_ff(chamber_volume: float) -> float:
            test_gun = self.get_gun(
                chamber_volume=chamber_volume, reduced_burnrates=tuple(1.0 for _ in self.propellants)
            )
            return test_gun.bomb_free_fraction - acc

        chamber_min_volume = self.chamber_min_volume

        bound = chamber_min_volume
        while f_ff(bound) <= 0:
            bound *= 2

        lower_limit = max(dekker(f=f_ff, x_0=chamber_min_volume, x_1=bound, tol=chamber_min_volume * acc))

        def f_p(chamber_volume: float) -> float:
            test_gun = self.get_gun(
                chamber_volume=chamber_volume, reduced_burnrates=tuple(1.0 for _ in self.propellants)
            )
            return pressure_target.get_difference(test_gun.get_bomb_state())

        if f_p(lower_limit) <= 0:
            raise ValueError("excessive pressure does not permit solution at given accuracy.")

        while f_p(bound) >= 0:
            bound *= 2

        upper_limit = min(dekker(f=f_p, x_0=lower_limit, x_1=bound, tol=chamber_min_volume * acc))

        logger.info(
            f"chamber volume limit for {pressure_target.describe()} solved to be "
            + f"{lower_limit * 1e3:.3f} L to {upper_limit * 1e3:.3f} L"
        )
        return lower_limit, upper_limit

    def solve_reduced_burn_rate_for_volume_at_pressure(
        self,
        chamber_volume: float,
        pressure_target: PressureTarget,
        reduced_burnrate_ratios: Optional[tuple[float, ...] | list[float]] = None,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
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
            parameter passed to `ballistics.gun.MonoChargeGun.to_burnout`. In addition, `acc`
            specifies the relative accuracy to which the reduced burn-rate is solved to,
            using an iterative procedure.

        Raises
        ------
        ValueError
            if the specified charge mass is either too low or too high for this
            gun design.

        Returns
        -------
        gun: `ballistics.gun.MonoChargeGun` object
            the gun corresponding to this solution.

        """

        logger.info(f"solve reduced burn rate for {pressure_target.describe()}")
        min_vol, max_vol = self.get_chamber_volume_limits(pressure_target=pressure_target, acc=acc)

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

        gun = self.get_gun_developing_pressure(
            charge_masses=self.charge_masses,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            chamber_volume=chamber_volume,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
        )
        logger.info(
            f"reduced burn rates solved to {", ".join(f"{charge.reduced_burnrate:.2e} s^-1" for charge in gun.charges)} "
        )
        return gun

    def get_guns_at_pressure(
        self,
        pressure_target: PressureTarget,
        reduced_burnrate_ratios: Optional[tuple[float, ...] | list[float]] = None,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
    ) -> tuple[Gun, Gun, Gun]:

        logger.info("getting limiting cases for" + f" {pressure_target.describe()}")

        vol_min, vol_max = self.get_chamber_volume_limits(pressure_target=pressure_target, acc=acc)

        def get_gun_with_volume(chamber_volume: float) -> Gun:
            return self.get_gun_developing_pressure(
                charge_masses=self.charge_masses,
                reduced_burnrate_ratios=reduced_burnrate_ratios,
                chamber_volume=chamber_volume,
                pressure_target=pressure_target,
                n_intg=n_intg,
                acc=acc,
            )

        def f(chamber_volume: float) -> float:
            gun = get_gun_with_volume(chamber_volume=chamber_volume)
            states = gun.to_travel(travel=self.travel, n_intg=n_intg, acc=acc)
            muzzle_state = states.get_state_by_marker(significance=Significance.MUZZLE)

            return muzzle_state.velocity

        vol_opt = sum(gss_max(f, x_0=vol_min, x_1=vol_max, tol=self.chamber_min_volume * acc)) * 0.5

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
        reduced_burnrate_ratios: Optional[tuple[float, ...] | list[float]] = None,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
    ) -> Tuple[Optional[Gun], Optional[Gun]]:

        logger.info("solve chamber volume for " + f"{velocity_target:.1f} m/s" + f"and {pressure_target.describe()}")

        gun_vol_min, gun_opt, gun_vol_max = self.get_guns_at_pressure(
            pressure_target=pressure_target,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            n_intg=n_intg,
            acc=acc,
        )

        def get_mv(gun: Gun) -> float:
            return gun.to_travel(n_intg=n_intg, acc=acc).muzzle_velocity

        v_vol_min = get_mv(gun_vol_min)
        v_vol_max = get_mv(gun_vol_max)
        v_opt = get_mv(gun_opt)

        v_min = min(v_vol_min, v_vol_max)
        logger.info(f"velocity from {v_min:.3f} and {v_opt:.3f} m/s")

        vol_min = gun_vol_min.chamber_volume
        vol_max = gun_vol_max.chamber_volume
        vol_opt = gun_opt.chamber_volume

        def f(chamber_volume: float) -> Gun:
            return self.get_gun_developing_pressure(
                charge_masses=self.charge_masses,
                reduced_burnrate_ratios=reduced_burnrate_ratios,
                chamber_volume=chamber_volume,
                pressure_target=pressure_target,
                n_intg=n_intg,
                acc=acc,
            )

        def g(vol_i: float, vol_j: float, v_i: float, v_j: float) -> Optional[Gun]:
            if min(v_i, v_j) <= velocity_target <= max(v_i, v_j):
                # target velocity is achievable, find the corresponding charge mass to get it.
                chamber_volume, _ = dekker(
                    f=lambda x: get_mv(f(x)) - velocity_target, x_0=vol_i, x_1=vol_j, tol=acc * self.chamber_min_volume
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
