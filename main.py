from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
from math import pi
from enum import Enum
from shape import FormFunction

_mm = 1e-3  # mm/m
_L = 1e-3  # liters/m^3
_ms = 1e-3  # ms/s


@dataclass
class Gun:
    """class keeping track of non-varying parameters of a gun design"""

    caliber: float

    def __post_init__(self):
        self.S = 0.25 * self.caliber**2 * pi
        self.loads = []

    def add_load(self, load: Load):
        self.loads.append(load)


@dataclass
class Load:
    """class that keeps track of particular load conditions"""

    gun: Gun
    shot_mass: float
    chamber_volume: float
    charges: Tuple[Charge]

    loss_fraction: float = 0.05

    def __post_init__(self):
        self.charge_mass = sum(c.charge_mass for c in self.charges)

        # calculate the average adiabatic index
        molar_sum = sum(c.charge_mass / c.gas_molar_mass for c in self.charges)
        average_Cp = 0
        average_Cv = 0
        for c in self.charges:
            adiabatic_index = c.adiabatic_index
            molar_fraction = (c.charge_mass / c.gas_molar_mass) / molar_sum
            average_Cp += molar_fraction * (adiabatic_index) / (adiabatic_index - 1)
            average_Cv += molar_fraction / (adiabatic_index - 1)

        self.average_adiabatic_index = average_Cp / average_Cv

        # calculation variables
        self.phi = 1 + self.loss_fraction + self.charge_mass / (3 * self.shot_mass)

    def __getattr__(self, item):
        return getattr(self.gun, item)

    def propagate_to_burnout(self, delta_t=1 * _ms):
        pass


@dataclass
class Charge:
    """class that represent individual charge designs"""

    load: Load
    propellant_density: float
    propellant_force: float  # J/kg
    burn_rate_coefficient: float
    pressure_exponent: float
    covolume: float
    adiabatic_index: float
    gas_molar_mass: float

    charge_mass: float
    arch_thickness: float

    form_function: FormFunction

    def __getattr__(self, item):
        return getattr(self.load, item)

    def psi_i(self, Z_i: float) -> float:
        return self.form_function(Z_i)

    def dZdt(self, P: float) -> float:
        return (
            self.burn_rate_coefficient / self.arch_thickness * P**self.pressure_exponent
        )

    def incompressible_fraction(self, psi_i: float) -> float:
        return ((1 - psi_i) / self.propellant_density + self.covolume * psi_i) * (
            (self.charge_mass / self.chamber_volume)
        )

    def gas_energy(self, psi_i: float) -> float:
        return self.propellant_force * self.charge_mass * psi_i


@dataclass
class State:
    time: float
    travel: float
    velocity: float
    burnup_fraction: Tuple[float]
    average_pressure: float


if __name__ == "__main__":

    g = Gun(0.1)
    print(g.S)
    pass
