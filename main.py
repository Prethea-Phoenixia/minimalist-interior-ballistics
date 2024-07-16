"""

list of notations:
    Z       : depth-wise burnup fraction. [0, Z_k].
    Z_k     : depth-wise burnup fraction for multi-perforated grains at end 
            of combustion. Z_k = 1 for non-/single-perforated grains
    psi     : volumetric burnup fraction. [0,1].
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional, List
from math import pi
from enum import Enum
from form_function_factory import FormFunction, single_perf
from dekker import dekker_scalar

_mm = 1e-3  # mm/m
_dm = 0.1  # dm/m
_L = _dm**3  # liters/m^3
_ms = 1e-3  # ms/s
_g_cc = 1e3  # kg/m^3
_cc_g = _g_cc**-1  # m^3/kg


def u_1_to_alpha(unitary_burn_rate: float, pressure_exponent: float) -> float:
    """
    convert unitary burn rate (dm^3/s-kgf) to burn rate coefficient (m/s-Pa^n)
    """
    return unitary_burn_rate * 9.8**-pressure_exponent * 1e-3


@dataclass
class Load:
    """class that keeps track of particular load conditions"""

    caliber: float
    shot_mass: float
    chamber_volume: float
    loss_fraction: float = 0.05
    start_pressure: float = 30e6

    def __post_init__(self):
        self.charges = []
        self.S = 0.25 * self.caliber**2 * pi
        self.l_0 = self.chamber_volume / self.S

    def add_charge(self, *args, **kwargs):
        self.charges.append(Charge(load=self, *args, **kwargs))
        self.total_charge_mass = sum(c.charge_mass for c in self.charges)
        # calculate the average adiabatic index
        molar_sum = sum(c.charge_mass / c.gas_molar_mass for c in self.charges)
        average_Cp = 0
        average_Cv = 0
        for c in self.charges:
            adiabatic_index = c.adiabatic_index
            molar_fraction = (c.charge_mass / c.gas_molar_mass) / molar_sum
            average_Cp += molar_fraction * (adiabatic_index) / (adiabatic_index - 1)
            average_Cv += molar_fraction / (adiabatic_index - 1)

        average_adiabatic_index = average_Cp / average_Cv
        self.theta = average_adiabatic_index - 1

        # calculation variables
        self.phi = (
            1 + self.loss_fraction + self.total_charge_mass / (3 * self.shot_mass)
        )

    def populate(self, delta_T=1 * _ms):
        Z_c0 = tuple(c.solve_bomb() for c in self.charges)
        print(Z_c0)
        s = State(time=0, travel=0, velocity=0, burnup_fractions=Z_c0)
        self.dt(s)

    def dt(self, state: State):
        t, l, v = state.time, state.travel, state.velocity
        m = self.shot_mass
        i_f = 0
        g_e = 0
        for c, Z_c in zip(self.charges, state.burnup_fractions):
            psi_c = c.psi_c(Z_c)
            i_f += c.incompressible_fraction(psi_c)
            g_e += c.gas_energy(psi_c)

        l_psi = self.l_0 * (1 - i_f)
        P = (g_e - 0.5 * self.theta * self.phi * m * v**2) / (self.S * (l_psi + l))

        dl = v
        dv = self.S * P / (self.phi * m)
        dZ = tuple(c.dZdt(P) for c in self.charges)


@dataclass
class State:
    time: float
    travel: float
    velocity: float
    burnup_fractions: Tuple[float]


@dataclass
class Gradient:
    d_time: float
    d_travel: float
    d_velocity: float
    d_burnup_fractions: Tuple[float]


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

    def psi_c(self, Z_c: float) -> float:
        return self.form_function(Z_c)

    def dZdt(self, P: float) -> float:
        return (
            self.burn_rate_coefficient / self.arch_thickness * P**self.pressure_exponent
        )

    def incompressible_fraction(self, psi_c: float) -> float:
        return ((1 - psi_c) / self.propellant_density + self.covolume * psi_c) * (
            (self.charge_mass / self.chamber_volume)
        )

    def gas_energy(self, psi_c: float) -> float:
        return self.propellant_force * self.charge_mass * psi_c

    def solve_bomb(self) -> float:
        V_c0 = self.chamber_volume * (self.charge_mass / self.total_charge_mass)
        P_0 = self.start_pressure
        m, f = self.charge_mass, self.propellant_force
        rho_p, alpha = self.propellant_density, self.covolume
        Delta = m / V_c0
        psi_0 = (Delta**-1 - rho_p**-1) / (f / P_0 + alpha - rho_p**-1)

        if P_max := f * Delta / (1 - alpha * Delta) < P_0:
            raise ValueError("Starting pressure is excessive compared to charge.")

        Z_0 = dekker_scalar(
            f=lambda z: self.form_function(z) - psi_0, x_0=0, x_1=1, tol=1e-3
        )
        return Z_0


if __name__ == "__main__":

    print(u_1_to_alpha(5.6298e-5, 0.83))
    zis_3 = Load(
        caliber=127 * _mm,
        shot_mass=6.2,
        chamber_volume=1.484 * _L,
        loss_fraction=0.03,
    )
    zis_3.add_charge(
        propellant_density=1.6 * _g_cc,
        propellant_force=950e3,
        pressure_exponent=0.83,
        covolume=1.0 * _cc_g,
        burn_rate_coefficient=u_1_to_alpha(5.6298e-5, 0.83),
        adiabatic_index=1.2,
        gas_molar_mass=23.55,
        charge_mass=1.08,
        arch_thickness=0.5e-02 * _dm,
        form_function=single_perf(arch_width=0.5e-3, length=0.12),
    )
    zis_3.populate()
    # print(l)
