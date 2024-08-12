from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from . import (DEFAULT_IGNITION_PRESSURE, DEFAULT_LOAD_DENSITY, MAX_DT,
               Significance)
from .bomb_state import BombDelta, BombState
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
        ```where:
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
        ```where:
        - u: burn rate coefficient, in m/s-Pa^n.
          - n: burn rate exponent, dimensionless.
        - 2e: width of the propellant arch.
    gas_molar_mass: float
        value used to calculate the average adiabatic index of a gas mixture.
        No particular unit is required, the only requirement being consistency across
        a set of `Charge` objects added to the same `ballistics.gun.Gun`. For the case
        of a single `Charge`, any value will work.


    Attributes
    ----------
    Z_k: float
        cached value from `ballistics.form_function.Z_k`.

    Notes
    -----
    the Saint Robert's (Viellie's) burn rate law:
    ```
    u = a * P^n
    ```where:
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
    form_function: FormFunction

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
            see documentation of `ballistics.form_function` for more information.
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

    @classmethod
    def from_areal_impulse(
        cls,
        density: float,
        force: float,
        pressure_exponent: float,
        covolume: float,
        adiabatic_index: float,
        gas_molar_mass: float,
        form_function: FormFunction,
        areal_impulse: float,
        n_intg: int,
        acc: float,
        load_density: float = DEFAULT_LOAD_DENSITY,
        ignition_pressure: float = DEFAULT_IGNITION_PRESSURE,
        to: Significance = Significance.FRACTURE,
    ) -> Charge:
        """
        define a Charge using areal impulse. Solves the reduced burn-rate
        from the supplied geometry, areal_impulse, and preessure exponent, exploiting
        the property of:
        ```
        dP/dt ∝ u/e -> I ∝ u/e
        ```

        Parameters
        ----------
        density, force, pressure_exponent, covolume, adiabatic_index, gas_molar_mass: float
            see documentation for `Charge`.
        areal_impulse: float
            areal_impulse per area until specified point, in kg/m-s.
        n_intg: int
            see documentation for `Charge.areal_impulse`.
        acc,  load_density, ignition_pressure, to: float
            see documentation for `Charge.areal_impulse`.
        to: `ballistics.Significance`
            see documentation for `Charge.areal_impulse`.
        """
        c_ubr = cls(
            density=density,
            force=force,
            reduced_burnrate=1,
            pressure_exponent=pressure_exponent,
            covolume=covolume,
            adiabatic_index=adiabatic_index,
            gas_molar_mass=gas_molar_mass,
            form_function=form_function,
        )  # initialize a charge with unit reduced burn rate

        I_ubr = c_ubr.areal_impulse(
            n_intg=n_intg,
            acc=acc,
            load_density=load_density,
            ignition_pressure=ignition_pressure,
            to=to,
        )
        return cls(
            density=density,
            force=force,
            reduced_burnrate=I_ubr / areal_impulse,
            pressure_exponent=pressure_exponent,
            covolume=covolume,
            adiabatic_index=adiabatic_index,
            gas_molar_mass=gas_molar_mass,
            form_function=form_function,
        )

    @cached_property
    def Z_k(self) -> float:
        return self.form_function.Z_k

    def psi_c(self, Z_c: float) -> float:
        return self.form_function(Z_c)

    def dZdt(self, P: float) -> float:
        return self.reduced_burnrate * P**self.pressure_exponent

    def areal_impulse(
        self,
        n_intg: int,
        acc: float,
        load_density: float = DEFAULT_LOAD_DENSITY,
        ignition_pressure: float = DEFAULT_IGNITION_PRESSURE,
        to: Significance = Significance.FRACTURE,
    ) -> float:
        """calculate the impulse-per-area of this propellant, as:
        ```
              t
        I =   ∫ P(t) dt
              0
        ```until the specified endpoint.

        Parameters
        ----------
        n_intg: int
            minimum number of steps taken from ignition to powder burnout.

        acc: float
            accuracy to which the ignition point is solved.

        load_density: float
            the density to which the test bomb is loaded with propellant. The
            default value of 0.2 g/cc (200 kg/m^3) is a common choice of loading
            density for characterizing propellant performance.

        ignition_pressure: float
            the pressure developed by the ignition charge, usually fine-grained
            black powder, which is taken as having fully burnt and inert during the
            characterization of propellant. The default value is the typical ignition
            pressure (of 100 kgf/sqcm) ascribed to by Chinese standardized testing
            procedures.

        to: `ballistics.Significance`
            specifies to whence the p-t curve is integrated. Accepts either
            `ballistics.Significance.BURNOUT` or `ballistics.Significance.FRACTURE`.
            This concerns propellants of the multiple-perforated type, for which period
            testing methodology only considers the combustion up to the fracture point.

        Notes
        -----
        In propellant development, the characterization of propellant performance is
        typically accomplished by a "closed-bomb" test, in which a sturdy pressure vessel
        is loaded to a certain weight-of-charge-per-volume, known as the "load density",
        then a small amount of ignition charge is used to initiate its combustion.
        Propellant performance parameters can then be derived via data reduction of the
        measured pressure-time curve.
        The default values reflects Chinese standardized testing methodology as of 1970s
        and 1980s.

        References
        ----------
        - **[中文]** 第五机械工业部第二〇四研究所，火炸药手册（增订本）第三分册 火炸药分析
        和测试，第五章第一节（1981.6)

        Returns
        -------
        I: float
            propellant's impulse-per-area up to the specified point. In unit of
            kg/m-s

        """
        if to == Significance.BURNOUT:
            Z_to = self.Z_k
        elif to == Significance.FRACTURE:
            Z_to = 1
        else:
            raise ValueError(
                "`to` must be one of `Significance.BURNOUT` or `Significance.FRACTURE`"
            )

        """integrate backwards in time from burnout point to avoid asymptotic
        point at t = 0, then read-off the time and impulse-values as negatives.
        """
        n, delta_t, rough_ttb = 0, MAX_DT, 0.0

        while n < n_intg:
            if rough_ttb > 0:
                delta_t = rough_ttb / n_intg
            n = 1

            bs_next = BombState(
                charge=self,
                load_density=load_density,
                ignition_pressure=ignition_pressure,
                time=0,
                burnup_fraction=0,
                areal_impulse=0,
            )

            while bs_next.burnup_fraction < Z_to:
                bs_now = bs_next
                bs_next = self.propagate_rk4(bomb_state=bs_now, dt=delta_t)
                n += 1

            rough_ttb = bs_next.time

        tol_t = rough_ttb * acc

        def time_burnup(time: float) -> float:
            return (
                self.propagate_rk4(
                    bomb_state=bs_now, dt=time - bs_now.time
                ).burnup_fraction
                - Z_to
            )

        time_to = dekker(f=time_burnup, x_0=bs_now.time, x_1=bs_next.time, tol=tol_t)[0]
        bs_to = self.propagate_rk4(bomb_state=bs_now, dt=time_to - bs_now.time)

        return bs_to.areal_impulse

    def dt(self, bomb_state: BombState) -> BombDelta:
        P = bomb_state.pressure
        return BombDelta(d_time=1, d_burnup_fraction=self.dZdt(P), d_areal_impulse=P)

    def propagate_rk4(self, bomb_state: BombState, dt: float) -> BombState:
        s_i = bomb_state.increment
        df = self.dt

        k1 = df(bomb_state)
        k2 = df(s_i(d=0.5 * k1 * dt, dt=0.5 * dt))
        k3 = df(s_i(d=0.5 * k2 * dt, dt=0.5 * dt))
        k4 = df(s_i(d=k3 * dt, dt=dt))
        return s_i(d=(k1 + k2 * 2 + k3 * 2 + k4) * dt / 6, dt=dt)
