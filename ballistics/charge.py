from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from .num import dekker
from .form_function import FormFunction

if TYPE_CHECKING:
    from .gun import Gun


@dataclass(frozen=True)
class BaseCharge:
    """class that represent individual charges as standalone designs."""

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

    @property
    def Z_k(self):
        return self.form_function.Z_k

    def psi_c(self, Z_c: float) -> float:
        return self.form_function(Z_c)

    def dZdt(self, P: float) -> float:
        return (
            2
            * self.burn_rate_coefficient
            * P**self.pressure_exponent
            / self.arch_thickness
        )

    def gas_energy(self, psi_c: float) -> float:
        return self.propellant_force * self.charge_mass * psi_c


@dataclass(frozen=True)
class Charge(BaseCharge):
    """class that represent individual charge designs when applied to a gun."""

    gun: Gun = field(repr=False)

    def __getattr__(self, item):
        return getattr(self.gun, item)

    def incompressible_fraction(self, psi_c: float) -> float:
        return ((1 - psi_c) / self.propellant_density + self.covolume * psi_c) * (
            (self.charge_mass / self.chamber_volume)
        )

    def solve_bomb(self, tol: float) -> float:
        V_c0 = self.chamber_volume * (self.charge_mass / self.total_charge_mass)
        P_0 = self.start_pressure
        m, f = self.charge_mass, self.propellant_force
        rho_p, alpha = self.propellant_density, self.covolume
        Delta = m / V_c0
        psi_0 = (Delta**-1 - rho_p**-1) / (f / P_0 + alpha - rho_p**-1)

        if f * Delta / (1 - alpha * Delta) < P_0:
            raise ValueError(
                "Charge cannot overcome starting pressure at complete combustion."
            )

        Z_0 = dekker(
            f=lambda z: self.form_function(z) - psi_0, x_0=0.0, x_1=1.0, tol=tol
        )[0]
        return Z_0
