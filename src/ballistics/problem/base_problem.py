from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from attrs import field, frozen

from .. import (DEFAULT_ACC, DEFAULT_GUN_LOSS_FRACTION,
                DEFAULT_GUN_START_PRESSURE, DEFAULT_STEPS,
                REDUCED_BURN_RATE_INITIAL_GUESS, Significance)
from ..charge import Charge, Propellant
from ..gun import MonoChargeGun
from ..num import dekker
from .pressure_target import PressureTarget

if TYPE_CHECKING:
    from ballistics.form_function import FormFunction

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class BaseProblem:
    name: str = field(default="")
    description: str = field(default="")
    family: str = field(default="")

    propellant: Propellant
    form_function: FormFunction

    cross_section: float
    shot_mass: float
    travel: float
    loss_fraction: float = DEFAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE

    def get_gun(self, *, charge_mass: float, chamber_volume: float, reduced_burnrate: float) -> MonoChargeGun:
        return MonoChargeGun(
            name=self.name,
            description=self.description,
            family=self.family,
            cross_section=self.cross_section,
            shot_mass=self.shot_mass,
            charge_mass=charge_mass,
            charge=Charge.from_propellant(
                reduced_burnrate=reduced_burnrate,
                propellant=self.propellant,
                form_function=self.form_function,
            ),
            chamber_volume=chamber_volume,
            travel=self.travel,
            loss_fraction=self.loss_fraction,
            start_pressure=self.start_pressure,
        )

    def get_gun_developing_pressure(
        self,
        *,
        charge_mass: float,
        chamber_volume: float,
        pressure_target: PressureTarget,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        logging_preamble: str = "",
    ) -> MonoChargeGun:

        # first, sanity check the pressure value is achievable:

        unitary_gun = self.get_gun(
            charge_mass=charge_mass,
            chamber_volume=chamber_volume,
            reduced_burnrate=1,
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
                reduced_burnrate=reduced_burnrate,
                charge_mass=charge_mass,
                chamber_volume=chamber_volume,
            )
            states = test_gun.to_burnout(
                n_intg=n_intg,
                acc=acc,
                abort_travel=self.travel,
                logging_preamble=logging_preamble + "\t",
            )
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

        logger.info(
            logging_preamble
            + f"CHARGE {charge_mass:.3f} kg CHAMBER {chamber_volume * 1e3:.3f} L"
            + f" -> REDUCED BURN RATE {est:.2e} s^-1 END"
        )

        return self.get_gun(reduced_burnrate=est, charge_mass=charge_mass, chamber_volume=chamber_volume)
