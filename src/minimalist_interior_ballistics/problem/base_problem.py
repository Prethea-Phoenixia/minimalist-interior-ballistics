from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional
from functools import wraps
from attrs import field, frozen
from .. import (
    DEFAULT_ACC,
    DEFAULT_GUN_LOSS_FRACTION,
    DEFAULT_GUN_START_PRESSURE,
    DEFAULT_STEPS,
    REDUCED_BURN_RATE_INITIAL_GUESS,
    Significance,
)
from ..charge import Charge, Propellant
from ..gun import Gun
from ..num import dekker
from .pressure_target import PressureTarget

if TYPE_CHECKING:
    from ..form_function import FormFunction

logger = logging.getLogger(__name__)


def accepts_charge_mass(func):
    @wraps(func)
    def handled_func(
        self: BaseProblem,
        *args,
        charge_mass: Optional[float] = None,
        charge_masses: Optional[list[float] | tuple[float, ...]] = None,
        **kwargs,
    ):
        if bool(charge_mass) == bool(charge_masses):
            raise ValueError("one and only one charge_mass or charge_masses must be supplied")
        if charge_mass:
            charge_masses = tuple([charge_mass])
        charge_masses = tuple(charge_masses)

        if len(charge_masses) != len(self.propellants):
            raise ValueError("charge_mass(es) must have same dimension as charge(s)")

        return func(self, *args, charge_masses=charge_masses, **kwargs)

    return handled_func


def accepts_reduced_burnrate(func):
    @wraps(func)
    def handled_func(
        self: BaseProblem,
        *args,
        reduced_burnrate: Optional[float] = None,
        reduced_burnrates: Optional[list[float] | tuple[float, ...]] = None,
        **kwargs,
    ):

        if bool(reduced_burnrates) == bool(reduced_burnrate):
            raise ValueError("one and only one reduced_burnrate or reduced_burnrates must be supplied")
        if reduced_burnrate:
            reduced_burnrates = tuple([reduced_burnrate])
        reduced_burnrates = tuple(reduced_burnrates)

        if len(reduced_burnrates) != len(self.propellants):
            raise ValueError("reduced_burnrate(s) must have same dimension as charge(s)")

        return func(self, *args, reduced_burnrates=reduced_burnrates, **kwargs)

    return handled_func


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
    acc: float = DEFAULT_ACC
    n_intg: int = DEFAULT_STEPS

    def __attrs_post_init__(self):
        if self.propellant and self.form_function:
            object.__setattr__(self, "propellants", tuple([self.propellant]))
            object.__setattr__(self, "form_functions", tuple([self.form_function]))

        if self.propellants and self.form_functions:
            if len(self.propellants) != len(self.form_functions):
                raise ValueError("mismatch for propellants and form_functions dimensions.")
        else:
            raise ValueError("invalid BaseProblem parameters.")

    @accepts_reduced_burnrate
    @accepts_charge_mass
    def get_gun(
        self, chamber_volume: float, charge_masses: tuple[float, ...], reduced_burnrates: tuple[float, ...]
    ) -> Gun:

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

    @accepts_charge_mass
    def get_gun_at_pressure(
        self,
        pressure_target: PressureTarget,
        chamber_volume: float,
        charge_masses: tuple[float, ...],
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
    ) -> Gun:

        main_charge_index = charge_masses.index(max(charge_masses))
        normalized_burn_rate_ratios = tuple(
            reduced_burnrate_ratio / reduced_burnrate_ratios[main_charge_index]
            for reduced_burnrate_ratio in reduced_burnrate_ratios
        )

        def get_burnrates(main_charge_reduced_burnrate: float) -> tuple[float, ...]:
            return tuple(nrbr * main_charge_reduced_burnrate for nrbr in normalized_burn_rate_ratios)

        unitary_gun = self.get_gun(
            charge_masses=charge_masses, chamber_volume=chamber_volume, reduced_burnrates=get_burnrates(1.0)
        )
        """exact burn rate doesn't matter here, so long as the equation can be propagated to
        generate a `State` object with the correct `State.average_pressure` (within numeric 
        accuracy), from which all the other conversions are deterministic."""

        if pressure_target.get_difference(unitary_gun.get_bomb_state()) < 0:
            raise ValueError("specified pressure is too high to achieve")
        elif pressure_target.get_difference(unitary_gun.get_start_state(n_intg=self.n_intg, acc=self.acc)) > 0:
            raise ValueError("specified pressure is less than the starting state.")

        def f(reduced_burnrate: float) -> float:
            test_gun = self.get_gun(
                reduced_burnrates=get_burnrates(reduced_burnrate),
                charge_masses=charge_masses,
                chamber_volume=chamber_volume,
            )
            states = test_gun.to_burnout(n_intg=self.n_intg, acc=self.acc, abort_travel=self.travel)
            delta_p = pressure_target.get_difference(states.get_state_by_marker(Significance.PEAK_PRESSURE))
            return delta_p

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
        then, use `minimalist_interior_ballistics.num.dekker` to find the exact solution. this is necessary
        since the accuracy specification is relative and the order of magnitude of the
        estimates aren't known a-priori
        """
        while abs(est - est_prime) > self.acc * min(est, est_prime):
            est, est_prime = dekker(f=f, x_0=est, x_1=est_prime, tol=min(est, est_prime) * self.acc)
        return self.get_gun(
            reduced_burnrates=get_burnrates(est), charge_masses=charge_masses, chamber_volume=chamber_volume
        )
