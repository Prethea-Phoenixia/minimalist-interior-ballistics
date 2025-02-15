from __future__ import annotations

import codecs
import csv
import logging
from functools import cached_property
from typing import Optional, Tuple

from attrs import field, frozen

from . import AMBIENT_PRESSURE
from .form_function import FormFunction

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class Propellant:
    """class that represent propellant before they are cut into gun charges.

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
        parameter in the Saint Robert's (Viellie's) burn rate law:
        ```
        u = a * P^n
        ```
        where:
        - u: linear burn rate, in m/s
        - a: burn rate coefficient, in m s^-1 Pa^-n.
          - n: pressure exponent, dimensionless.
        - P: average chamber pressure, in Pa.
        is used to model the combustion behavior of the propellant.
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

    Attributes
    ----------
    theta: float
        adiabatic index - 1.

    References
    ----------
    - **[English]** Xu, Fu-ming. (2013). On The Definition of Propellant Force.
    Defence Technology. 9. 127-130. 10.1016/j.dt.2013.10.005.

    """

    name: str = field(default="")
    description: str = field(default="")
    burn_rate_coefficient: Optional[float] = field(default=None)
    density: float = field(default=1600)
    force: float
    pressure_exponent: float = field(default=0.82)
    covolume: float = field(default=1e-3)
    adiabatic_index: float = field(default=1.2)

    @cached_property
    def theta(self) -> float:
        return self.adiabatic_index - 1

    @staticmethod
    def from_csv_file(file_name: str) -> Tuple[Propellant, ...]:
        prop_list = []
        with open(file_name, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                try:
                    (
                        adiabatic_index,
                        density,
                        force,
                        covolume,
                        pressure_exponent,
                        burn_rate_coefficient,
                    ) = row[2:]

                    name, description = row[:2]

                    prop_list.append(
                        Propellant(
                            name=name,
                            description=codecs.decode(description, "unicode_escape"),
                            adiabatic_index=float(adiabatic_index),
                            density=float(density),
                            force=float(force),
                            covolume=float(covolume),
                            pressure_exponent=float(pressure_exponent),
                            burn_rate_coefficient=(float(burn_rate_coefficient) if burn_rate_coefficient else None),
                        )
                    )

                except ValueError as e:
                    logger.warn("skipped line in propellant definition: " + str(e))

                # print(", ".join(row))
        return tuple(prop_list)


@frozen(kw_only=True)
class Charge(Propellant):
    """class that represent particular charge design.

    Parameters
    ----------
    density, force, pressure_exponent, covolume, adiabatic_index: float
        see documentation for `Propellant`.
    reduced_burnrate: float
        the burn-rate coefficient is factored against the propellant's arch,
        to produce the `reduced burn rate`, defined as:
        ```
        a / e
        ```
        where:
        - a: burn rate coefficient, in m Pa^-n s^-1.
          - n: burn rate exponent, dimensionless.
        - 2e: width of the propellant arch.
    form_function: `ballistics.form_function.FormFunction`
        form function that describes the shape of charge.

    Attributes
    ----------
    Z_k: float
        cached value from `ballistics.form_function.FormFunction.Z_k`.
    theta: float
        see documentation for `Propellant`

    References
    ----------
    - **[English]** Xu, Fu-ming. (2013). On The Definition of Propellant Force.
    Defence Technology. 9. 127-130. 10.1016/j.dt.2013.10.005.

    """

    reduced_burnrate: float  # u_1 / e_1
    form_function: FormFunction

    @classmethod
    def from_propellant(
        cls,
        *,
        reduced_burnrate: float,
        propellant: Propellant,
        form_function: FormFunction,
        description: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Charge:
        """
        defines a charge with propellant and reduced burn rate.

        Parameters
        ----------
        reduced_burnrate: float
            see documentation of `ballistics.form_function.FormFunction` for more information.
        propellant: `Propellant`
            base propellant of this charge.
        form_function:
            `ballistics.form_function.FormFunction` object that describes the geometry of this
            propellant.

        Notes
        -----
        For convenience, functions to estimate the reduced burn rate has been provided, as
        `Charge.estimate_reduced_from_coefficient_and_arch` and
        `Charge.estimate_reduced_from_unitary_and_arch`, and their use is strongly encouraged.

        """

        return cls(
            name=" ".join((propellant.name, form_function.name)) if name is None else name,
            description=form_function.description if description is None else description,
            density=propellant.density,
            force=propellant.force,
            pressure_exponent=propellant.pressure_exponent,
            covolume=propellant.covolume,
            adiabatic_index=propellant.adiabatic_index,
            reduced_burnrate=reduced_burnrate,
            form_function=form_function,
        )

    @staticmethod
    def estimate_reduced_from_coefficient_and_arch(*, arch_width: float, burn_rate_coefficient: float) -> float:
        """
        Parameters
        ----------
        arch_width: float
            twice the propellant's "web", or the minimum depth the propellant's
            burn surface must recede to achieve a "burnthrough".
            See documentation of `ballistics.form_function.FormFunction` for more
            information.
        burn_rate_coefficient: float
            coefficient used in de Saint Robert's burn rate law.
            See documentation for `Charge` for more information.

        Notes
        -----
        Tabulating the propellant's burn rate this way is particularly common with Western sources
        and more recent work fromChina.
        """
        return 2 * burn_rate_coefficient / arch_width

    def get_coefficient_from_arch(self, arch_width: float) -> float:
        return 0.5 * self.reduced_burnrate * arch_width

    @cached_property
    def Z_k(self) -> float:
        return self.form_function.Z_k

    def psi(self, Z: float) -> float:
        return self.form_function(Z)

    def dZdt(self, P: float) -> float:
        return self.reduced_burnrate * max(P, AMBIENT_PRESSURE) ** self.pressure_exponent
