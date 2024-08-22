from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import log10
from typing import TYPE_CHECKING, Dict, List, Tuple

from . import (DEFAULT_GUN_IGNITION_PRESSURE, DEFAULT_GUN_START_PRESSURE,
               DFEAULT_GUN_LOSS_FRACTION, Significance)
from .charge import Charge
from .gun import Gun
from .num import Find, dekker, gss, secant

if TYPE_CHECKING:
    from .state import State
    from .form_function import FormFunction


class Target(Enum):
    BREECH = "breech_pressure"
    AVERAGE = "average_pressure"
    SHOT = "shot_pressure"


@dataclass(frozen=True)
class MatchingProblem:
    """
    Given known gun and charge loading parameters, deduce the (additional) charge
    that is required to *match* the performance, in terms of peak pressure and
    shot velocity.
    """

    density: float
    force: float
    pressure_exponent: float
    covolume: float
    adiabatic_index: float
    gas_molar_mass: float
    form_function: FormFunction

    caliber: float
    shot_mass: float
    chamber_volume: float
    travel: float
    loss_fraction: float = DFEAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE
    ignition_pressure: float = DEFAULT_GUN_IGNITION_PRESSURE

    known_charge_loads: Dict[Charge, float] = field(default_factory=dict)

    def __post_init__(self):
        if self.get_base_gun().bomb_free_fraction < 0:
            raise ValueError("pre-existing charges for this gun design is overfull")

    def get_base_gun(self) -> Gun:
        gun = Gun(
            caliber=self.caliber,
            shot_mass=self.shot_mass,
            chamber_volume=self.chamber_volume,
            loss_fraction=self.loss_fraction,
            start_pressure=self.start_pressure,
            ignition_pressure=self.ignition_pressure,
        )

        for charge, mass in self.known_charge_loads.items():
            gun.set_charge(charge=charge, mass=mass)

        return gun

    def get_test_gun(self, reduced_burnrate: float, mass: float) -> Gun:
        gun = self.get_base_gun()
        charge = Charge(
            density=self.density,
            force=self.force,
            pressure_exponent=self.pressure_exponent,
            covolume=self.covolume,
            adiabatic_index=self.adiabatic_index,
            reduced_burnrate=reduced_burnrate,
            gas_molar_mass=self.gas_molar_mass,
            form_function=self.form_function,
        )
        gun.set_charge(charge=charge, mass=mass)
        return gun

    def get_charge_mass_limits(
        self, pressure: float, target: Target, acc: float
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

        The overfull condition refers to where the bomb-pressure of a charge design
        goes to infinity. This is an artifact of using a constant covolume correction
        parameter in the Nobel-Abel equation of state, where the growth in density
        exhausts the incompressibility. Realistically, this is only achieved well past
        the applicability of the applicability of this assumed EoS, where more accurate
        EoS for high pressure (such as Virial, etc) should be used.

        In any event, the use of Nobel-Abel EoS requires a cut-off point to be set for
        charge mass, so that even in case of infinitesimally high reduced burn rate
        coeffcient, the interior ballistic system of equation is not applied outside
        of its domain. On first glance, this limitation might seem overly conservative,
        as there exist solutions at or above the cut-off charge loading, that employs
        a lower burn-rate coefficient, such that at no point would the incompressibility
        be exhausted.

        #TODO: write this

        """
        base_gun = self.get_base_gun()

        def f_ff(mass: float) -> float:
            test_gun = self.get_test_gun(reduced_burnrate=1, mass=mass)
            return test_gun.bomb_free_fraction

        chamber_fill_mass = (
            base_gun.chamber_volume - base_gun.total_charge_volume
        ) * self.density

        upper_limit = min(
            dekker(f_ff, 0, chamber_fill_mass, tol=chamber_fill_mass * acc)
        )

        def f_p(mass: float) -> float:
            # note this is defined on [0, chamber_fill_mass]
            test_gun = self.get_test_gun(reduced_burnrate=1, mass=mass)
            test_gun_bomb_pressure = getattr(test_gun.get_bomb_state(), target.value)
            return test_gun_bomb_pressure - pressure

        if f_p(0) > 0:
            lower_limit = 0.0
        else:
            lower_limit = max(dekker(f_p, 0, upper_limit, tol=acc * upper_limit))

        return lower_limit, upper_limit

    def solve_reduced_burn_rate(
        self,
        velocity: float,
        mass: float,
        pressure: float,
        target: Target,
        n_intg: int,
        acc: float,
    ) -> Gun:

        min_mass, max_mass = self.get_charge_mass_limits(
            pressure=pressure, target=target, acc=acc
        )

        print(min_mass, max_mass)

        if mass < min_mass:
            raise ValueError(
                "specified charge cannot possibly develop the targeted pressure."
            )
        elif mass > max_mass:
            raise ValueError("specified charge is excessive for this chamber design.")

        def get_test_gun(reduced_burnrate: float) -> Gun:
            return self.get_test_gun(reduced_burnrate=reduced_burnrate, mass=mass)

        def f(reduced_burnrate: float) -> float:
            test_gun = get_test_gun(reduced_burnrate=reduced_burnrate)
            states = test_gun.to_burnout(
                n_intg=n_intg, acc=acc, abort_travel=self.travel
            )
            pp = getattr(
                states.get_state_by_marker(Significance.PEAK_PRESSURE), target.value
            )
            result = pp - pressure
            print(reduced_burnrate, pp, result)
            return result

        # solve the burn rate coefficient on (0, +inf)
        est, est_prime = 10.0, 0.1  # arbitrary initial guesses
        while abs(est - est_prime) > acc * min(est, est_prime):
            est, est_prime = secant(
                f=f, x_0=est, x_1=est_prime, x_min=0, tol=min(est, est_prime) * acc
            )
        gun = get_test_gun(reduced_burnrate=est)

        print(Gun.tabulate(gun.to_travel(travel=self.travel, n_intg=n_intg, acc=acc)))

        return gun
