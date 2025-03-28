from __future__ import annotations

import logging
from typing import Optional, Tuple

from attrs import frozen
from ballistics import DEFAULT_ACC, DEFAULT_STEPS, Significance
from ballistics.gun import Gun
from ballistics.num import dekker, gss_max
from ballistics.problem.base_problem import BaseProblem
from ballistics.problem.pressure_target import PressureTarget

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class FixedVolumeProblem(BaseProblem):
    """
    Given known gun and charge loading parameters, deduce the charge that is required to *match*
    the performance, in terms of peak pressure and shot velocity.
    """

    chamber_volume: float

    @classmethod
    def from_base_problem(cls, base_problem: BaseProblem, chamber_volume: float) -> FixedVolumeProblem:
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
            chamber_volume=chamber_volume,
        )

    def get_gun(
        self,
        *,
        charge_mass: Optional[float] = None,
        charge_masses: Optional[list[float] | tuple[float, ...]] = None,
        reduced_burnrate: Optional[float] = None,
        reduced_burnrates: Optional[list[float] | tuple[float, ...]] = None,
        **kwargs,
    ) -> Gun:

        if charge_mass and reduced_burnrate:
            charge_masses = tuple([charge_mass])
            reduced_burnrates = tuple([reduced_burnrate])

        if charge_masses and reduced_burnrates:
            if len(charge_masses) == len(reduced_burnrates) == len(self.propellants):
                pass
            else:
                raise ValueError(
                    "charge_masses and reduced_burnrates must have the same dimension as self.propellants and form_functions"
                )
        else:
            raise ValueError("invalid parameters.")

        return super().get_gun(
            reduced_burnrates=reduced_burnrates,
            charge_masses=charge_masses,
            chamber_volume=self.chamber_volume,
        )

    def get_fill_mass(self, charge_mass_ratios: list[float] | tuple[float, ...]) -> float:
        average_density = sum(charge_mass_ratios) / sum(
            charge_mass / propellant.density for charge_mass, propellant in zip(charge_mass_ratios, self.propellants)
        )
        return self.chamber_volume * average_density

    def get_charge_masses(
        self, total_charge_mass, charge_mass_ratios: list[float] | tuple[float, ...]
    ) -> tuple[float, ...]:
        if len(charge_mass_ratios) != len(self.propellants):
            raise ValueError("charge_mass_ratios must have the same dimension as self.propellants and form_functions")

        normalized_charge_mass_ratios = tuple(
            [charge_mass / sum(charge_mass_ratios) for charge_mass in charge_mass_ratios]
        )
        return tuple(charge_mass_ratio * total_charge_mass for charge_mass_ratio in normalized_charge_mass_ratios)

    def get_charge_mass_limits(
        self,
        pressure_target: PressureTarget,
        acc: float = DEFAULT_ACC,
        charge_mass_ratios: list[float] | tuple[float, ...] = tuple([1]),
    ) -> tuple[float, float]:
        """
        Find the maximum and minimum valid charge mass value for the outlined gun design

        Parameters
        ----------
        pressure_target, acc: `ballistics.problem.pressure_target.PressureTarget`, float
            see `ballistics.problem.base_problem.BaseProblem.get_gun_at_pressure`
            for more information.

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
        chamber reduces volumetric free fraction to less than `acc`, since the Nobel-Abel
        equation of state does not model high pressure (and correspondingly
        high incompressibility) well.

        The reduced-burn rate that corresponds to the limiting charge
        weights asymptotically approaches `+inf` for the lower limit, and 0 for the
        upper limit. Care is taken such that the returned limits, being numerically
        solved, errs on the conservative side.
        """
        logger.info("get charge mass limits")

        def f_ff(total_charge_mass: float) -> float:
            test_gun = self.get_gun(
                charge_masses=self.get_charge_masses(
                    total_charge_mass=total_charge_mass, charge_mass_ratios=charge_mass_ratios
                ),
                reduced_burnrates=tuple(1.0 for _ in self.propellants),
            )
            return test_gun.bomb_free_fraction - acc

        chamber_fill_mass = self.get_fill_mass(charge_mass_ratios=charge_mass_ratios)
        upper_limit = min(dekker(f_ff, 0, chamber_fill_mass, tol=chamber_fill_mass * acc))

        # up until this point execution is guaranteed.

        def f_p(total_charge_mass: float) -> float:
            # note this is defined on [0, chamber_fill_mass]
            test_gun = self.get_gun(
                charge_masses=self.get_charge_masses(
                    total_charge_mass=total_charge_mass, charge_mass_ratios=charge_mass_ratios
                ),
                reduced_burnrates=tuple(1.0 for _ in self.propellants),
            )
            return pressure_target.get_difference(test_gun.get_bomb_state())

        if f_p(upper_limit) <= 0:
            raise ValueError("excessive pressure target does not permit solution at given accuracy.")

        lower_limit = max(dekker(f_p, 0, upper_limit, tol=chamber_fill_mass * acc))

        logger.info(
            f"charge mass limit for {pressure_target.describe()} solved to be "
            + f"{lower_limit:.3f} kg to {upper_limit:.3f} kg"
        )

        return lower_limit, upper_limit

    def solve_reduced_burn_rate_for_charge_at_pressure(
        self,
        pressure_target: PressureTarget,
        charge_mass: Optional[float] = None,
        charge_masses: Optional[list[float] | tuple[float, ...]] = None,
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        **kwargs,
    ) -> Gun:
        """
        solves the reduced burn rate such that the peak pressure developed in bore
        matches the desired value. This is the outer, user facing function that validates
        the input by checking against the calcualted charge mass limits. Implementation
        instead under `ballistics.problem.base_problem.BaseProblem.get_gun_at_pressure`
        method.

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

        logger.info(f"solve reduced burn rate for {pressure_target.describe()}")

        if charge_mass:
            charge_masses = tuple([charge_mass])

        if charge_masses:
            if not (len(charge_masses) == len(self.propellants)):
                raise ValueError(
                    "charge_masses and reduced_burnrate_ratios must have the same dimension as self.propellants and form_functions"
                )
        else:
            raise ValueError("invalid parameters.")

        min_mass, max_mass = self.get_charge_mass_limits(
            pressure_target=pressure_target,
            acc=acc,
            charge_mass_ratios=charge_masses,
        )

        valid_range_prompt = f"valid range of charge mass: [{min_mass:.3f}, {max_mass:.3f}]"
        if sum(charge_masses) < min_mass:
            raise ValueError("specified charge cannot possibly develop the targeted pressure.\n" + valid_range_prompt)
        elif sum(charge_masses) > max_mass:
            raise ValueError("specified charge exceed maximum load density considered.\n" + valid_range_prompt)

        gun = self.get_gun_at_pressure(
            charge_masses=charge_masses,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            chamber_volume=self.chamber_volume,
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
        charge_mass_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
    ) -> Tuple[Gun, Gun, Gun]:

        logger.info("getting limiting cases for" + f" {pressure_target.describe()}")

        mass_min, mass_max = self.get_charge_mass_limits(
            pressure_target=pressure_target, charge_mass_ratios=charge_mass_ratios, acc=acc
        )

        def get_gun_with_charge_mass(total_charge_mass: float) -> Gun:
            return self.get_gun_at_pressure(
                charge_masses=self.get_charge_masses(
                    total_charge_mass=total_charge_mass, charge_mass_ratios=charge_mass_ratios
                ),
                reduced_burnrate_ratios=reduced_burnrate_ratios,
                chamber_volume=self.chamber_volume,
                pressure_target=pressure_target,
                n_intg=n_intg,
                acc=acc,
            )

        def f(total_charge_mass: float) -> float:
            gun = get_gun_with_charge_mass(total_charge_mass=total_charge_mass)
            states = gun.to_travel(travel=self.travel, n_intg=n_intg, acc=acc)
            muzzle_state = states.get_state_by_marker(significance=Significance.MUZZLE)

            return muzzle_state.velocity

        chamber_fill_mass = self.get_fill_mass(charge_mass_ratios=charge_mass_ratios)

        mass_opt = sum(gss_max(f=f, x_0=mass_min, x_1=mass_max, tol=chamber_fill_mass * acc)) * 0.5

        results = (
            get_gun_with_charge_mass(total_charge_mass=mass_min),
            get_gun_with_charge_mass(total_charge_mass=mass_opt),
            get_gun_with_charge_mass(total_charge_mass=mass_max),
        )

        logger.info(f"optimal charge mass {mass_opt:.3f} kg")

        return results

    def solve_charge_mass_at_pressure_for_velocity(
        self,
        pressure_target: PressureTarget,
        velocity_target: float,
        charge_mass_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
    ) -> Tuple[Optional[Gun], Optional[Gun]]:

        logger.info("solve charge mass for " + f"{velocity_target:.1f} m/s" + f"and {pressure_target.describe()}")

        gun_mass_min, gun_opt, gun_mass_max = self.get_guns_at_pressure(
            pressure_target=pressure_target,
            charge_mass_ratios=charge_mass_ratios,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            n_intg=n_intg,
            acc=acc,
        )

        mass_min = gun_mass_min.gross_charge_mass
        mass_max = gun_mass_max.gross_charge_mass
        mass_opt = gun_opt.gross_charge_mass

        def get_mv(gun: Gun) -> float:
            return gun.to_travel(n_intg=n_intg, acc=acc).muzzle_velocity

        v_mass_min = get_mv(gun_mass_min)
        v_mass_max = get_mv(gun_mass_max)
        v_min = min(v_mass_min, v_mass_max)
        v_max = get_mv(gun_opt)
        logger.info(f"velocity from {v_min:.3f} to {v_max:.3f} m/s")

        chamber_fill_mass = self.get_fill_mass(charge_mass_ratios=charge_mass_ratios)

        def f(charge_mass: float) -> Gun:
            gun = self.get_gun_at_pressure(
                charge_masses=self.get_charge_masses(
                    total_charge_mass=charge_mass, charge_mass_ratios=charge_mass_ratios
                ),
                reduced_burnrate_ratios=reduced_burnrate_ratios,
                chamber_volume=self.chamber_volume,
                pressure_target=pressure_target,
                n_intg=n_intg,
                acc=acc,
            )
            return gun

        def g(mass_i: float, mass_j: float, v_i: float, v_j: float) -> Optional[Gun]:
            if min(v_i, v_j) <= velocity_target <= max(v_i, v_j):
                # target velocity is achievable, find the corresponding charge mass to get it.
                charge_mass, _ = dekker(
                    f=lambda x: get_mv(f(x)) - velocity_target, x_0=mass_i, x_1=mass_j, tol=acc * chamber_fill_mass
                )
                gun = f(charge_mass=charge_mass)
                return gun
            else:
                return None

        results = (
            g(mass_i=mass_min, mass_j=mass_opt, v_i=v_mass_min, v_j=v_max),
            g(mass_i=mass_opt, mass_j=mass_max, v_i=v_max, v_j=v_mass_max),
        )

        logger.info(
            "low charge mass "
            + (f"{results[0].gross_charge_mass:.3f} kg " if results[0] else "impossible ")
            + "high charge mass "
            + (f"{results[1].gross_charge_mass:.3f} kg " if results[1] else "impossible ")
        )
        return results
