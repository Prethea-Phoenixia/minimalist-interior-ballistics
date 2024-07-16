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


def unitary_to_exponent(unitary_burn_rate: float, pressure_exponent: float) -> float:
    """
    convert unitary burn rate (dm^3/s-kgf) to burn rate coefficient (m/s-Pa^n)
    """
    return unitary_burn_rate * 1e-3 * 9.8**-pressure_exponent


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

        self.average_adiabatic_index = average_Cp / average_Cv

        # calculation variables
        self.phi = (
            1 + self.loss_fraction + self.total_charge_mass / (3 * self.shot_mass)
        )

    def populate(self, delta_t=0.1 * _ms):
        Z_c0 = tuple(c.solve_bomb() for c in self.charges)
        print(Z_c0)
        s = State(time=0, travel=0, velocity=0, burnup_fractions=Z_c0)
        print(s)
        for i in range(100):
            s = self.propagate_rk4_in_time(s, delta_t)
            print(s)

        print(s)

    def dt(self, state: State) -> Delta:
        l, v = state.travel, state.velocity
        m = self.shot_mass
        theta = self.average_adiabatic_index - 1
        i_f, g_e = 0, 0
        for c, Z_c in zip(self.charges, state.burnup_fractions):
            psi_c = c.psi_c(Z_c)
            i_f += c.incompressible_fraction(psi_c)
            g_e += c.gas_energy(psi_c)

        l_psi = self.l_0 * (1 - i_f)
        P = (g_e - 0.5 * theta * self.phi * m * v**2) / (self.S * (l_psi + l))

        return Delta(
            d_time=0,
            d_travel=v,
            d_velocity=self.S * P / (self.phi * m),
            d_burnup_fractions=tuple(c.dZdt(P) for c in self.charges),
        )

    def propagate_rk4_in_time(self, state: State, dt: float) -> State:
        k1 = self.dt(state)
        k2 = self.dt(state.increment_time(d=0.5 * k1 * dt, dt=0.5 * dt))
        k3 = self.dt(state.increment_time(d=0.5 * k2 * dt, dt=0.5 * dt))
        k4 = self.dt(state.increment_time(d=k3 * dt, dt=dt))
        return state.increment_time(d=(k1 + k2 * 2 + k3 * 2 + k4) * dt / 6, dt=dt)


@dataclass
class State:
    time: float
    travel: float
    velocity: float
    burnup_fractions: Tuple[float, ...]

    def increment_time(self, d: Delta, dt: float) -> State:
        return State(
            time=self.time + dt,
            travel=self.travel + d.d_travel,
            velocity=self.velocity + d.d_velocity,
            burnup_fractions=tuple(
                Z + dZ for Z, dZ in zip(self.burnup_fractions, d.d_burnup_fractions)
            ),
        )


@dataclass
class Delta:
    d_time: float
    d_travel: float
    d_velocity: float
    d_burnup_fractions: Tuple[float, ...]

    def __mul__(self, scalar: float) -> Delta:
        return Delta(
            d_time=self.d_time * scalar,
            d_travel=self.d_travel * scalar,
            d_velocity=self.d_velocity * scalar,
            d_burnup_fractions=tuple(dZ * scalar for dZ in self.d_burnup_fractions),
        )

    def __add__(self, other: Delta) -> Delta:
        return Delta(
            d_time=self.d_time + other.d_time,
            d_travel=self.d_travel + other.d_travel,
            d_velocity=self.d_velocity + other.d_velocity,
            d_burnup_fractions=tuple(
                v + w for v, w in zip(self.d_burnup_fractions, other.d_burnup_fractions)
            ),
        )

    def __rmul__(self, scalar: float) -> Delta:
        return self * scalar

    def __truediv__(self, scalar: float) -> Delta:
        return self * (1 / scalar)


@dataclass
class Charge:
    """class that represent individual charge designs"""

    load: Load
    propellant_density: float
    propellant_force: float
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
            self.burn_rate_coefficient
            / (0.5 * self.arch_thickness)
            * P**self.pressure_exponent
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

    wb004p = Load(
        caliber=100 * _mm, shot_mass=15.6, chamber_volume=7.741 * _L, loss_fraction=0.06
    )
    ff = single_perf(arch_width=0.17e-2, length=26e-2)
    wb004p.add_charge(
        propellant_density=1600,
        propellant_force=980000,
        pressure_exponent=0.75,
        covolume=1e-3,
        burn_rate_coefficient=0.18e-2 / (1e6) ** 0.75,
        adiabatic_index=1.2,
        gas_molar_mass=23.55,
        charge_mass=5.6,
        arch_thickness=0.17e-2,
        form_function=ff,
    )
    wb004p.populate()
