from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from attrs import field, frozen
from ballistics import (DEFAULT_ACC, DEFAULT_GUN_LOSS_FRACTION,
                        DEFAULT_GUN_START_PRESSURE, DEFAULT_STEPS,
                        REDUCED_BURN_RATE_INITIAL_GUESS, Significance)
from ballistics.charge import Charge, Propellant
from ballistics.gun import Gun
from ballistics.num import dekker
from ballistics.problem.pressure_target import PressureTarget

if TYPE_CHECKING:
    from ballistics.form_function import FormFunction

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class BaseProblem:
    name: str = field(default="")
    description: str = field(default="")
    family: str = field(default="")

    propellant: Optional[Propellant] = None
    propellants: list[Propellant] | tuple[Propellant, ...] = tuple()

    form_function: Optional[FormFunction] = None
    form_functions: list[FormFunction] | tuple[FormFunction, ...] = tuple()

    cross_section: float
    shot_mass: float
    travel: float
    loss_fraction: float = DEFAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE

    def __attrs_post_init__(self):
        if self.propellant and self.form_function:
            object.__setattr__(self, "propellants", tuple([self.propellant]))
            object.__setattr__(self, "form_functions", tuple([self.form_function]))

        if self.propellants and self.form_functions:
            if len(self.propellants) != len(self.form_functions):
                raise ValueError("propellants and form_functions length mismatch")
        else:
            raise ValueError("invalid BaseProblem parameters")

    @classmethod
    def from_base_problem(cls, base_problem: BaseProblem, *args, **kwargs) -> BaseProblem:
        raise NotImplementedError("from_base_problem is undefined for BaseProblem")

    def get_gun(
        self,
        *,
        chamber_volume: float,
        charge_mass: Optional[float] = None,
        charge_masses: Optional[tuple[float, ...] | list[float]] = None,
        reduced_burnrate: Optional[float] = None,
        reduced_burnrates: Optional[tuple[float, ...] | list[float]] = None,
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

        return Gun(
            name=self.name,
            description=self.description,
            family=self.family,
            cross_section=self.cross_section,
            shot_mass=self.shot_mass,
            charges=tuple(
                Charge.from_propellant(
                    reduced_burnrate=reduced_burnrate, propellant=propellant, form_function=form_function
                )
                for propellant, form_function, reduced_burnrate in zip(
                    self.propellants, self.form_functions, reduced_burnrates
                )
            ),
            charge_masses=charge_masses,
            chamber_volume=chamber_volume,
            travel=self.travel,
            loss_fraction=self.loss_fraction,
            start_pressure=self.start_pressure,
        )

    def get_gun_developing_pressure(
        self,
        pressure_target: PressureTarget,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        *,
        chamber_volume: float,
        charge_mass: Optional[float] = None,
        charge_masses: Optional[tuple[float, ...] | list[float]] = None,
        reduced_burnrate_ratios: Optional[tuple[float, ...] | list[float]] = None,
    ) -> Gun:

        if charge_mass:
            charge_masses = tuple([charge_mass])

        if not reduced_burnrate_ratios:
            reduced_burnrate_ratios = tuple([1.0])

        if charge_masses and reduced_burnrate_ratios:
            if len(charge_masses) == len(reduced_burnrate_ratios) == len(self.propellants):
                pass
            else:
                raise ValueError(
                    "charge_masses and reduced_burnrate_ratios must have the same dimension as self.propellants and form_functions"
                )
        else:
            raise ValueError("invalid parameters.")

        # first, sanity check the pressure value is achievable:

        main_charge_index = charge_masses.index(max(charge_masses))
        normalized_burn_rate_ratios = tuple(
            reduced_burnrate_ratio / reduced_burnrate_ratios[main_charge_index]
            for reduced_burnrate_ratio in reduced_burnrate_ratios
        )

        def get_burnrates(main_charge_redueced_burnrate: float) -> tuple[float, ...]:
            return tuple(nrbr * main_charge_redueced_burnrate for nrbr in normalized_burn_rate_ratios)

        unitary_gun = self.get_gun(
            charge_masses=charge_masses, chamber_volume=chamber_volume, reduced_burnrates=get_burnrates(1.0)
        )
        """exact burn rate doesn't matter here, so long as the equation can be propagated to
        generate a `State` object with the correct `State.average_pressure` (within numeric 
        accuracy), from which all the other conversions are deterministic."""

        if pressure_target.get_difference(unitary_gun.get_bomb_state()) < 0:
            raise ValueError("specified pressure is too high to achieve")
        elif pressure_target.get_difference(unitary_gun.get_start_state(n_intg=n_intg, acc=acc)) > 0:
            raise ValueError("specified pressure is less than the starting state.")

        def f(reduced_burnrate: float) -> float:
            test_gun = self.get_gun(
                reduced_burnrates=get_burnrates(reduced_burnrate),
                charge_masses=charge_masses,
                chamber_volume=chamber_volume,
            )
            states = test_gun.to_burnout(n_intg=n_intg, acc=acc, abort_travel=self.travel)
            # logger.info(states.tabulate())
            delta_p = pressure_target.get_difference(states.get_state_by_marker(Significance.PEAK_PRESSURE))
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
        return self.get_gun(
            reduced_burnrates=get_burnrates(est), charge_masses=charge_masses, chamber_volume=chamber_volume
        )
