from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional, Tuple

from attrs import asdict, frozen

from .. import Significance
from ..gun import Gun
from ..num import dekker, gss_max
from .base_problem import BaseProblem, accepts_charge_mass, accepts_reduced_burnrate
from .pressure_target import PressureTarget

if TYPE_CHECKING:
    # these are required for pdoc to locate the references
    # noinspection PyUnresolvedReferences
    from ..charge import Propellant

    # noinspection PyUnresolvedReferences
    from ..form_function import FormFunction

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
        return cls(**asdict(base_problem, recurse=False), chamber_volume=chamber_volume)

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
        charge_mass_ratios: list[float] | tuple[float, ...] = tuple([1]),
    ) -> tuple[float, float]:
        """
        Find the maximum and minimum valid charge mass value for the outlined gun design

        Parameters
        ----------
        charge_mass_ratios: list[float] | tuple[float, ...]
            if more than one charge is specified, it is required to input the ratio of charge masses.
        pressure_target: `minimalist_interior_ballistics.problem.pressure_target.PressureTarget`, float
            see `minimalist_interior_ballistics.problem.base_problem.BaseProblem.get_gun_at_pressure`
            for more information.

        Returns
        -------
        lower_limit, upper_limit: float

        Notes
        -----
        The bomb-pressure refers to the pressure developed in a gun as its charges
        have completely burnt, before the projectile has moved. This corresponds
        to the case where the reduced burn-rate is infinitely high. It has the
        convenient property of being the maximum pressure that can be developed with
        a certain charge loading.

        The lower limit is found by finding the required mass of charge to bring the
        gun's bomb-pressure to the required level. The upper limit is found when the
        complete combustion of charge within chamber reduces volumetric free fraction
        to less than a reasonable level, conveniently chosen to be `acc`.

        In reality, designs falling close to either limits are highly undesirable,
        as the reduced-burn rate corresponding to the limiting charge weights asymptotically
        approaches `+inf` for the lower charge mass limit, and 0 for the upper limit.
        The former case approximates the interior ballistics for a pre-burned (light gas) gun,
        while the latter case usually implies unreasonable pressure levels.

        Since the returned results are required for further numerical solving, care is
        taken that the returned results are fudged on the conservative side, to ensure
        the interior ballistics system is always solved in domain.
        """
        logger.info("get charge mass limits")

        def f_ff(total_charge_mass: float) -> float:
            test_gun = self.get_gun(
                chamber_volume=self.chamber_volume,
                charge_masses=self.get_charge_masses(
                    total_charge_mass=total_charge_mass, charge_mass_ratios=charge_mass_ratios
                ),
                reduced_burnrates=tuple(1.0 for _ in self.propellants),
            )
            return test_gun.bomb_free_fraction - self.acc

        chamber_fill_mass = self.get_fill_mass(charge_mass_ratios=charge_mass_ratios)
        upper_limit = min(dekker(f=f_ff, x_0=0, x_1=chamber_fill_mass, tol=chamber_fill_mass * self.acc))

        safe_target = pressure_target * (1 + self.acc)

        def f_p(total_charge_mass: float) -> float:
            test_gun = self.get_gun(
                chamber_volume=self.chamber_volume,
                charge_masses=self.get_charge_masses(
                    total_charge_mass=total_charge_mass, charge_mass_ratios=charge_mass_ratios
                ),
                reduced_burnrates=tuple(1.0 for _ in self.propellants),
            )
            return safe_target.get_difference(test_gun.get_bomb_state())

        lower_limit = max(dekker(f_p, x_0=0, x_1=upper_limit, tol=chamber_fill_mass * self.acc))

        logger.info(
            f"charge mass limit for {pressure_target.describe()} solved to be "
            + f"{lower_limit:.3f} kg to {upper_limit:.3f} kg"
        )

        return lower_limit, upper_limit

    @accepts_charge_mass
    def solve_reduced_burn_rate_for_charge_at_pressure(
        self,
        pressure_target: PressureTarget,
        charge_masses=tuple[float, ...],
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
    ) -> Gun:
        """
        solves the reduced burn rate such that the peak pressure developed in bore
        matches the desired value. This is the outer, user facing function that validates
        the input by checking against the calcualted charge mass limits. Implementation
        instead under `minimalist_interior_ballistics.problem.base_problem.BaseProblem.get_gun_at_pressure`
        method.

        Parameters
        ----------
        charge_masses, reduced_burnrate_ratios: list[float] | tuple[float, ...]
            if more than one charge is specified, then it is also required that the mass for each, and the
            ratio of reduced burnrates be provided.
        pressure_target: float, `minimalist_interior_ballistics.problem.pressure_target.PressureTarget`
            the pressure to target, along with its point-of-measurement.

        Raises
        ------
        ValueError
            if the specified charge mass is either too low or too high for this
            gun design.

        Returns
        -------
        gun: `minimalist_interior_ballistics.gun.Gun` object
            the gun corresponding to this solution.

        """

        logger.info(f"solve reduced burn rate for {pressure_target.describe()}")

        min_mass, max_mass = self.get_charge_mass_limits(
            pressure_target=pressure_target, charge_mass_ratios=charge_masses
        )

        valid_range_prompt = f"valid range of charge mass: [{min_mass:.3f}, {max_mass:.3f}]"
        if sum(charge_masses) < min_mass:
            raise ValueError("specified charge cannot possibly develop the targeted pressure.\n" + valid_range_prompt)
        elif sum(charge_masses) > max_mass:
            raise ValueError("specified charge exceed maximum load density considered.\n" + valid_range_prompt)

        gun = self.get_gun_at_pressure(
            chamber_volume=self.chamber_volume,
            charge_masses=charge_masses,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            pressure_target=pressure_target,
        )
        logger.info(
            "reduced burn rates solved to " + ", ".join(f"{charge.reduced_burnrate:.2e} s^-1" for charge in gun.charges)
        )

        return gun

    def get_limiting_guns_at_pressure(
        self,
        pressure_target: PressureTarget,
        charge_mass_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
    ) -> Tuple[Gun, Gun, Gun]:

        logger.info("getting limiting cases for" + f" {pressure_target.describe()}")

        mass_min, mass_max = self.get_charge_mass_limits(
            pressure_target=pressure_target, charge_mass_ratios=charge_mass_ratios
        )

        def get_gun_with_charge_mass(total_charge_mass: float) -> Gun:
            return self.get_gun_at_pressure(
                chamber_volume=self.chamber_volume,
                charge_masses=self.get_charge_masses(
                    total_charge_mass=total_charge_mass, charge_mass_ratios=charge_mass_ratios
                ),
                reduced_burnrate_ratios=reduced_burnrate_ratios,
                pressure_target=pressure_target,
            )

        def f(total_charge_mass: float) -> float:
            gun = get_gun_with_charge_mass(total_charge_mass=total_charge_mass)
            states = gun.to_travel(travel=self.travel, n_intg=self.n_intg, acc=self.acc)
            muzzle_state = states.get_state_by_marker(significance=Significance.MUZZLE)

            return muzzle_state.velocity

        chamber_fill_mass = self.get_fill_mass(charge_mass_ratios=charge_mass_ratios)

        mass_opt = sum(gss_max(f=f, x_0=mass_min, x_1=mass_max, tol=chamber_fill_mass * self.acc)) * 0.5

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
    ) -> Tuple[Optional[Gun], Optional[Gun]]:

        logger.info(f"solve charge mass for {velocity_target:.1f} m/s and {pressure_target.describe()}")

        gun_mass_min, gun_opt, gun_mass_max = self.get_limiting_guns_at_pressure(
            pressure_target=pressure_target,
            charge_mass_ratios=charge_mass_ratios,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
        )

        mass_min = gun_mass_min.gross_charge_mass
        mass_max = gun_mass_max.gross_charge_mass
        mass_opt = gun_opt.gross_charge_mass

        def get_mv(gun: Gun) -> float:
            return gun.to_travel(travel=self.travel, n_intg=self.n_intg, acc=self.acc).muzzle_velocity

        v_mass_min = get_mv(gun_mass_min)
        v_mass_max = get_mv(gun_mass_max)
        v_min = min(v_mass_min, v_mass_max)
        v_max = get_mv(gun_opt)
        logger.info(f"velocity from {v_min:.3f} to {v_max:.3f} m/s")

        chamber_fill_mass = self.get_fill_mass(charge_mass_ratios=charge_mass_ratios)

        def f(charge_mass: float) -> Gun:
            gun = self.get_gun_at_pressure(
                chamber_volume=self.chamber_volume,
                charge_masses=self.get_charge_masses(
                    total_charge_mass=charge_mass, charge_mass_ratios=charge_mass_ratios
                ),
                reduced_burnrate_ratios=reduced_burnrate_ratios,
                pressure_target=pressure_target,
            )
            return gun

        def g(mass_i: float, mass_j: float, v_i: float, v_j: float) -> Optional[Gun]:
            if min(v_i, v_j) <= velocity_target <= max(v_i, v_j):
                # target velocity is achievable, find the corresponding charge mass to get it.
                charge_mass, _ = dekker(
                    f=lambda x: get_mv(f(x)) - velocity_target, x_0=mass_i, x_1=mass_j, tol=self.acc * chamber_fill_mass
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
