from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import log10
from typing import TYPE_CHECKING, Dict, List, Tuple

from . import (DEFAULT_GUN_IGNITION_PRESSURE,
               DEFAULT_GUN_MAX_GROSS_LOAD_DENSITY,
               DEFAULT_GUN_MIN_GROSS_LOAD_DENSITY, DEFAULT_GUN_START_PRESSURE,
               DFEAULT_GUN_LOSS_FRACTION, Significance)
from .charge import Charge
from .gun import Gun

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

    min_gross_load_density: float = DEFAULT_GUN_MIN_GROSS_LOAD_DENSITY
    max_gross_load_density: float = DEFAULT_GUN_MAX_GROSS_LOAD_DENSITY

    @property
    def min_charge_mass(self) -> float:
        gun = self.get_base_gun()
        return gun.chamber_volume * self.min_gross_load_density - gun.total_charge_mass

    @property
    def max_charge_mass(self):
        gun = self.get_base_gun()
        return gun.chamber_volume * self.max_gross_load_density - gun.total_charge_mass

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

    def solve(
        self,
        velocity: float,
        mass: float,
        pressure: float,
        target: Target,
        n_intg: int,
        acc: float,
    ) -> Gun:

        if mass < self.min_charge_mass or mass > self.max_charge_mass:
            raise ValueError("mass specified violates gross load density constraint.")

        def get_test_gun(reduced_burnrate: float) -> Gun:
            return self.get_test_gun(reduced_burnrate=reduced_burnrate, mass=mass)

        gun = get_test_gun(1)

        if pressure > getattr(gun.get_bomb_state(), target.value):
            raise ValueError("targeted pressure is impossible to achieve")

        # for i in range(8):
        #     rbr = 1e-6 * 10**i
        #     gun = add_test_charge(rbr)
        #     print(gun.bomb_pressure / 1e6)
        #     states = gun.to_burnout(abort_travel=self.travel, n_intg=n_intg, acc=acc)
        #     print(rbr)
        #     print(gun.tabulate(states))
