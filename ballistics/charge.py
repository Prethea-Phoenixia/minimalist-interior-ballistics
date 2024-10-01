from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from . import AMBIENT_PRESSURE, MAX_DT, Significance
from .form_function import FormFunction
from .num import dekker


@dataclass(frozen=True)
class Charge:
    """class that represent individual charges as standalone designs.

    Parameters
    ----------
    density: float
        bulk density of the propellant, in kg/m^3. Reported value is close to
        1600 kg/m^3 for various modern, smokeless/nitrocellulose based propellant.
    force: float
        propellant force, or the work done by a kilogram of propellant gas (as
        ideal gas), when expanding from its isochoric adiabatic flame temperature
        to absolute zero, in an isentropic manner. Unit in J/kg, or (m/s)^2.
    pressure_exponent: float
        see the Notes section.
    covolume: float
        the co-volume of a propellant, as used in the Nobel-Abel equation of state:
        ```
        P (v-alpha) = RT
        ```
        where:
        - P: average pressure in Pa.
        - v: specific volume of propellant gas, in m^3/kg.
        - alpha: covolume, in m^3/kg.
        - R: specific gas constant, in J/(kg-K).
        - T: average temprature in K.
    adiabatic_index: float
        the (average) heat capacity ratio of the working gas while in-bore.
        At elevated temperatures and with a mix of species, this parameter typically
        clusters around 1.23-1.25.
    reduced_burnrate: float
        the burn-rate coefficient is factored against the propellant's arch,
        to produce the `reduced burn rate`, defined as:
        ```
        u / e
        ```
        where:
        - u: burn rate coefficient, in m/s-Pa^n.
          - n: burn rate exponent, dimensionless.
        - 2e: width of the propellant arch.
    gas_molar_mass: float
        value used to calculate the average adiabatic index of a gas mixture.
        No particular unit is required, the only requirement being consistency across
        a set of `Charge` objects added to the same `ballistics.gun.Gun`. For the case
        of a single `Charge`, any value will work.
    form_function: Optional[`ballistics.form_function.FormFunction`]
        form function that describes the shape of charge.


    Attributes
    ----------
    Z_k: float
        cached value from `ballistics.form_function.Z_k`.

    Notes
    -----
    the Saint Robert's (Viellie's) burn rate law:
    ```
    u = a * P^n
    ```
    where:
    - u: linear burn rate, in m/s
    - a: burn rate coefficient, in m/(s-Pa^n).
      - n: pressure exponent, dimensionless.
    - P: average chamber pressure, in Pa.
    is used to model the combustion behavior of the propellant.

    References
    ----------
    - **[English]** Xu, Fu-ming. (2013). On The Definition of Propellant Force.
    Defence Technology. 9. 127-130. 10.1016/j.dt.2013.10.005.

    """

    density: float
    force: float
    pressure_exponent: float
    covolume: float
    adiabatic_index: float
    reduced_burnrate: float  # u_1 / e_1
    gas_molar_mass: float
    form_function: Optional[FormFunction]

    @classmethod
    def from_dimension_and_burnrate(
        cls,
        density: float,
        force: float,
        pressure_exponent: float,
        covolume: float,
        adiabatic_index: float,
        gas_molar_mass: float,
        form_function: FormFunction,
        arch_width: float,
        burn_rate_coefficient: float,
    ) -> Charge:
        """
        defines a charge using the measurement of arch thickness in conjunction with
        burn rate coefficient data.

        Parameters
        ----------
        density, force, pressure_exponent, covolume, adiabatic_index, gas_molar_mass: float
            see documentation for `Charge`.
        arch_width: float
            twice the propellant's "web", or the minimum depth the propellant's
            burn surface must recede to achieve a "burnthrough".
            see documentation of `ballistics.form_function.FormFunction` for more
            information.
        burn_rate_coefficient: float
            coefficient used in de Saint Robert's burn rate law. See documentation for
            `Charge` for more information.
        """
        return cls(
            density=density,
            force=force,
            pressure_exponent=pressure_exponent,
            covolume=covolume,
            adiabatic_index=adiabatic_index,
            gas_molar_mass=gas_molar_mass,
            reduced_burnrate=2 * burn_rate_coefficient / arch_width,
            form_function=form_function,
        )

    @cached_property
    def Z_k(self) -> float:
        return self.form_function.Z_k

    def psi_c(self, Z_c: float) -> float:
        return self.form_function(Z_c)

    def dZdt(self, P: float) -> float:
        return self.reduced_burnrate * max(P, AMBIENT_PRESSURE) ** self.pressure_exponent
