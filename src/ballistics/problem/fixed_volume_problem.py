from __future__ import annotations

import logging
# from functools import cached_property
from typing import TYPE_CHECKING, Optional, Tuple

from attrs import frozen

from .. import DEFAULT_ACC, DEFAULT_STEPS, Significance
from ..gun import Gun
from ..num import dekker, gss_max
from .base_problem import BaseProblem
from .pressure_target import PressureTarget

if TYPE_CHECKING:
    # these are required for pdoc
    from ..charge import FormFunction, Propellant

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class FixedVolumeProblem(BaseProblem):
    """
    Given known gun and charge loading parameters, deduce the charge that is required to *match*
    the performance, in terms of peak pressure and shot velocity.
    """

    chamber_volume: float

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

    def get_charge_mass_limits(
        self,
        pressure_target: PressureTarget,
        acc: float = DEFAULT_ACC,
        charge_mass_ratios: Optional[list[float] | tuple[float, ...]] = None,
        logging_preamble: str = "",
    ) -> Tuple[float, float]:
        """
        Find the maximum and minimum valid charge mass value for the outlined gun design

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

        if not charge_mass_ratios:
            charge_mass_ratios = tuple([1])

        if charge_mass_ratios:
            if len(charge_mass_ratios) != len(self.propellants):
                raise ValueError("charge_masses must have same dimension as self.propellants and form_functions")
        else:
            raise ValueError("invalid parameters.")

        normalized_charge_mass_ratios = tuple(
            [charge_mass / max(charge_mass_ratios) for charge_mass in charge_mass_ratios]
        )

        def get_masses(charge_mass: float) -> tuple[float, ...]:
            return tuple(charge_mass_ratio * charge_mass for charge_mass_ratio in normalized_charge_mass_ratios)

        def f_ff(charge_mass: float) -> float:
            test_gun = self.get_gun(
                charge_masses=get_masses(charge_mass), reduced_burnrates=tuple(0 for _ in self.propellants)
            )
            return test_gun.bomb_free_fraction - acc

        chamber_fill_mass = self.get_fill_mass(charge_mass_ratios=charge_mass_ratios)
        upper_limit = min(dekker(f_ff, 0, chamber_fill_mass, tol=chamber_fill_mass * acc))

        # up until this point execution is guaranteed.

        def f_p(charge_mass: float) -> float:
            # note this is defined on [0, chamber_fill_mass]
            test_gun = self.get_gun(
                charge_masses=get_masses(charge_mass), reduced_burnrates=tuple(0 for _ in self.propellants)
            )
            return pressure_target.get_difference(test_gun.get_bomb_state())

        if f_p(upper_limit) <= 0:
            raise ValueError("excessive pressure target does not permit solution at given accuracy.")

        lower_limit = max(dekker(f_p, 0, upper_limit, tol=chamber_fill_mass * acc))
        logger.info(
            logging_preamble
            + f"CHARGE LIMIT {pressure_target.describe()} -> "
            + f"CHARGE {lower_limit:.3f} kg TO {upper_limit:.3f} kg END"
        )
        return lower_limit, upper_limit

    def solve_reduced_burn_rate_for_charge_at_pressure(
        self,
        pressure_target: PressureTarget,
        charge_mass: Optional[float] = None,
        charge_masses: Optional[list[float] | tuple[float, ...]] = None,
        reduced_burnrate_ratios: Optional[list[float] | tuple[float, ...]] = None,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        logging_preamble: str = "",
        **kwargs,
    ) -> Gun:
        """
        solves the reduced burn rate such that the peak pressure developed in bore
        matches the desired value. This is the outer, user facing function that validates
        the input by checking against the calcualted charge mass limits. Implementation
        instead under `ballistics.problem.base_problem.BaseProblem.get_gun_developing_pressure`
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

        if charge_mass:
            charge_masses = tuple([charge_mass])

        if charge_masses:
            if not (len(charge_masses) == len(self.propellants)):
                raise ValueError(
                    "charge_masses and reduced_burnrate_ratios must have the same dimension as self.propellants and form_functions"
                )
        else:
            raise ValueError("invalid parameters.")

        logger.info(logging_preamble + f"MATCH PRESSURE PROBLEM {pressure_target.describe()} ->")
        min_mass, max_mass = self.get_charge_mass_limits(
            pressure_target=pressure_target,
            acc=acc,
            logging_preamble=logging_preamble + "\t",
            charge_mass_ratios=charge_masses,
        )

        valid_range_prompt = f"valid range of charge mass: [{min_mass:.3f}, {max_mass:.3f}]"
        if sum(charge_masses) < min_mass:
            raise ValueError("specified charge cannot possibly develop the targeted pressure.\n" + valid_range_prompt)
        elif sum(charge_masses) > max_mass:
            raise ValueError("specified charge exceed maximum load density considered.\n" + valid_range_prompt)

        gun = self.get_gun_developing_pressure(
            charge_masses=charge_masses,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            chamber_volume=self.chamber_volume,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
            logging_preamble=logging_preamble + "\t",
        )
        logger.info(
            logging_preamble
            + f"->REDUCED BURN RATES {", ".join(f"{charge.reduced_burnrate:.2e} s^-1" for charge in gun.charges)} END"
        )

        return gun

    def solve_charge_mass_at_pressure_for_velocity(
        self,
        pressure_target: PressureTarget,
        charge_mass_ratios: Optional[list[float] | tuple[float, ...]] = None,
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
        mass_min, mass_max = self.get_charge_mass_limits(
            pressure_target=pressure_target,
            charge_mass_ratios=charge_mass_ratios,
            acc=acc,
            logging_preamble=logging_preamble + "\t",
        )

        if not charge_mass_ratios:
            charge_mass_ratios = tuple([1])

        if charge_mass_ratios:
            if len(charge_mass_ratios) != len(self.propellants):
                raise ValueError(
                    "charge_mass_ratios must have the same dimension as self.propellants and form_functions"
                )
        else:
            raise ValueError("invalid parameters.")

        normalized_charge_mass_ratios = tuple(
            [charge_mass / max(charge_mass_ratios) for charge_mass in charge_mass_ratios]
        )

        def get_masses(charge_mass: float) -> tuple[float, ...]:
            return tuple(charge_mass_ratio * charge_mass for charge_mass_ratio in normalized_charge_mass_ratios)

        def get_gun_with_charge_mass(charge_mass: float) -> Gun:
            return self.get_gun_developing_pressure(
                charge_masses=get_masses(charge_mass),
                chamber_volume=self.chamber_volume,
                pressure_target=pressure_target,
                n_intg=n_intg,
                acc=acc,
                logging_preamble=logging_preamble + "\t",
            )

        def f(charge_mass: float) -> float:
            gun = get_gun_with_charge_mass(charge_mass=charge_mass)
            states = gun.to_travel(travel=self.travel, n_intg=n_intg, acc=acc, logging_preamble=logging_preamble + "\t")
            muzzle_state = states.get_state_by_marker(significance=Significance.MUZZLE)

            return muzzle_state.velocity

        v_mass_min = f(charge_mass=mass_min)
        v_mass_max = f(charge_mass=mass_max)

        chamber_fill_mass = self.get_fill_mass(charge_mass_ratios=charge_mass_ratios)

        mass_opt = sum(gss_max(f=f, x_0=mass_min, x_1=mass_max, tol=chamber_fill_mass * acc)) * 0.5
        v_min = min(v_mass_min, v_mass_max)
        v_max = f(mass_opt)

        logger.info(logging_preamble + f"-> VELOCITY RANGE {v_min:.3f} TO {v_max:.3f} m/s")

        if velocity_target:
            if not v_min <= velocity_target <= v_max:
                raise ValueError("targeted velocity is not achievable in the range of valid loading condition.")

            def g(mass_i: float, mass_j: float, v_i: float, v_j: float) -> Optional[Gun]:
                if v_i - velocity_target <= 0 <= v_j - velocity_target:
                    # target velocity is achievable, find the corresponding charge mass to get it.
                    charge_mass, _ = dekker(
                        f=lambda x: f(x) - velocity_target, x_0=mass_i, x_1=mass_j, tol=acc * chamber_fill_mass
                    )
                    gun = get_gun_with_charge_mass(charge_mass=charge_mass)

                    logger.info(
                        logging_preamble
                        + f"-> CHARGE {charge_mass:.3f} kg, "
                        + f"REDUCED BURN RATES {", ".join(f"{charge.reduced_burnrate:.2e} s^-1" for charge in gun.charges)} END"
                    )
                    return gun
                else:
                    return None

            logger.info(logging_preamble + "END")
            return (
                g(mass_i=mass_min, mass_j=mass_opt, v_i=v_mass_min, v_j=v_max),
                None,
                g(mass_i=mass_opt, mass_j=mass_max, v_i=v_max, v_j=v_mass_max),
            )
        else:  # no velocity target is specified.
            return (
                get_gun_with_charge_mass(charge_mass=mass_min),
                get_gun_with_charge_mass(charge_mass=mass_opt),
                get_gun_with_charge_mass(charge_mass=mass_max),
            )
