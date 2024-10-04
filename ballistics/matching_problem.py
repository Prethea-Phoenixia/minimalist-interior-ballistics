from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Tuple

from . import (DEFAULT_GUN_START_PRESSURE, DFEAULT_GUN_LOSS_FRACTION,
               Significance)
from .charge import Charge, Propellant
from .gun import Gun
from .num import dekker
from .pressure_target import PressureTarget

if TYPE_CHECKING:
    from .form_function import FormFunction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MatchingProblem:
    """
    Given known gun and charge loading parameters, deduce the (additional) charge
    that is required to *match* the performance, in terms of peak pressure and
    shot velocity.
    """

    propellant: Propellant
    form_function: FormFunction

    cross_section: float
    shot_mass: float
    chamber_volume: float
    travel: float
    loss_fraction: float = DFEAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE

    # known_charge_loads: Dict[Charge, float] = field(default_factory=dict)

    def __post_init__(self):
        if self.get_base_gun().bomb_free_fraction < 0:
            raise ValueError("pre-existing charges for this gun design is overfull")

    def get_test_gun(self, reduced_burnrate: float, mass: float) -> Gun:
        charge = Charge.from_propellant(
            reduced_burnrate=reduced_burnrate,
            propellant=self.propellant,
            form_function=self.form_function,
        )

        gun = Gun(
            cross_section=self.cross_section,
            shot_mass=self.shot_mass,
            charge_mass=mass,
            charge=charge,
            chamber_volume=self.chamber_volume,
            loss_fraction=self.loss_fraction,
            start_pressure=self.start_pressure,
        )
        return gun

    def get_base_gun(self):
        return self.get_test_gun(reduced_burnrate=1, mass=0)

    def get_charge_mass_limits(
        self, pressure_target: PressureTarget, acc: float
    ) -> Tuple[float, float]:
        """
        Find the maximum and minimum valid charge mass value for the outlined gun design

        Parameters
        ----------
        pressure, target, acc: float, Target, float
            see `MatchingProblem.solve_reduced_burn_rate` for more information.

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

        The upper limit is found by finding the point at which the bomb-pressure of
        a charge design goes to infinity. This is an artifact of the limited
        applicability of the Nobel-Abel equation of state for very high pressures.

        The reduced-burn rate that corresponds to the limiting charge
        weights asymptotically approaches `+inf` for the lower limit, and 0 for the
        upper limit. Care is taken such that the returned limits, being numerically
        solved, errs on the conservative side.
        """
        base_gun = self.get_base_gun()

        def f_ff(mass: float) -> float:
            test_gun = self.get_test_gun(reduced_burnrate=1, mass=mass)
            return test_gun.bomb_free_fraction

        chamber_fill_mass = (
            base_gun.chamber_volume - base_gun.charge_volume
        ) * self.propellant.density

        upper_limit = min(dekker(f_ff, 0, chamber_fill_mass, tol=chamber_fill_mass * acc))

        def f_p(mass: float) -> float:
            # note this is defined on [0, chamber_fill_mass]
            test_gun = self.get_test_gun(reduced_burnrate=1, mass=mass)
            test_gun_bomb_pressure = pressure_target.retrieve_from(test_gun.get_bomb_state())
            return test_gun_bomb_pressure - pressure_target.value

        if f_p(0) > 0:
            lower_limit = 0.0
        else:
            lower_limit = max(dekker(f_p, 0, upper_limit, tol=acc * upper_limit))

        logger.info(f"charge limit solved to be {lower_limit} kg, {upper_limit} kg.")
        return lower_limit, upper_limit

    def solve_reduced_burn_rate(
        self, mass: float, pressure_target: PressureTarget, n_intg: int, acc: float
    ) -> Tuple[float, Gun]:
        """
        solves the reduced burn rate such that the peak pressure developed in bore
        (at any one of the three `ballistics.problem.Target` locations)
        matches the desired value.

        Parameters
        ----------
        mass: float
            the mass of the charge.
        pressure, target: float, `ballistics.problem.Target`
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
        reduced_burnrate: float
            the solved reduced burnrate.
        gun: `ballistics.gun.Gun` object
            the gun corresponding to this solution.
        """

        min_mass, max_mass = self.get_charge_mass_limits(pressure_target=pressure_target, acc=acc)
        valid_range_prompt = f"valid range of charge mass: [{min_mass:.3f}, {max_mass:.3f}]"
        if mass < min_mass:
            raise ValueError(
                "specified charge cannot possibly develop the targeted pressure.\n"
                + valid_range_prompt
            )
        elif mass > max_mass:
            raise ValueError(
                "specified charge is excessive for this chamber design.\n" + valid_range_prompt
            )

        def get_test_gun(reduced_burnrate: float) -> Gun:
            return self.get_test_gun(reduced_burnrate=reduced_burnrate, mass=mass)

        def f(reduced_burnrate: float) -> float:
            test_gun = get_test_gun(reduced_burnrate=reduced_burnrate)
            states = test_gun.to_burnout(n_intg=n_intg, acc=acc, abort_travel=self.travel)

            return (
                pressure_target.retrieve_from(
                    states.get_state_by_marker(Significance.PEAK_PRESSURE)
                )
                - pressure_target.value
            )

        # solve the burn rate coefficient on (0, +inf)

        """
        first, find two estimate, est and est' (rendered as est_prime) such that
        the solution is bracketed
        """
        est = est_prime = 1.0
        f_est = f_est_prime = f(est)
        while f_est * f_est_prime >= 0:
            if f_est > 0:  # burnt too fast
                est, est_prime = est / 10, est  # reduce rbr by 1 oom
            elif f_est == 0:  # this is *exceedingly* unlikely to happen but still.
                est, est_prime = est / 10, est * 10
            else:
                est, est_prime = est * 10, est
            f_est, f_est_prime = f(est), f_est

        logger.info(f"roughly estimated reduced burn rate between {est} and {est_prime}")

        """
        then, use `ballistics.num.dekker` to find the exact solution. this is necessary
        since the accuracy specification is realtive and the order of magnitude of the
        estimates aren't known a-priori
        """
        while abs(est - est_prime) > acc * min(est, est_prime):
            est, est_prime = dekker(f=f, x_0=est, x_1=est_prime, tol=min(est, est_prime) * acc)

        logger.info(f"reduced burn rate solved at {est}")
        return est, get_test_gun(reduced_burnrate=est)
