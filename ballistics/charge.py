from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from . import MAX_DT
from .num import dekker
from .form_function import FormFunction
from functools import wraps, cached_property

if TYPE_CHECKING:
    from .gun import Gun


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
        to absolute zero, in an isentropic manner (see [1]). Unit in J/kg, or (m/s)^2.
    burn_rate_coefficient, pressure_exponent: float
        the two coefficients of the Saint Robert's (Viellie's) burn rate law:
        ```
        u = a * P^n
        ```
        where:
        - u: linear burn rate, in m/s
        - a: burn rate coefficient, in m s^-1 Pa^-n
        - P: average chamber pressure, in Pa
        - n: pressure exponent, dimensionless.
    covolume: float
        the co-volume of a propellant, as used in the Nobel-Abel equation of state:
        ```
        P (v-alpha) = RT
        ```
        where:
        - P: average pressure in Pa
        - v: specific volume of propellant gas, in m^3/kg
        - alpha: covolume, in m^3/kg
        - R: specific gas constant, in J/(kg-K)
        - T: average temprature in K
    adiabatic_index: float
        the (average) heat capacity ratio of the working gas while in-bore.
        At elevated temperatures and with a mix of species, this parameter typically
        clusters around 1.23-1.25.
    gas_molar_mass: float
        value used to calculate the average adiabatic index of a gas mixture.
        No particular unit is required, the only requirement being consistency across
        a set of `Charge` objects added to the same `ballistics.gun.Gun`. For the case
        of a single `Charge`, any value will work.
    arch_thickness: float
        twice the propellant's "web", or the minimum depth the propellant's burn surface
        must recede to complete combustion.
        see `ballistics.form_function` for more information.

    References
    ----------
    - **[1]** Xu, Fu-ming. (2013). On The Definition of Propellant Force.
    Defence Technology. 9. 127-130. 10.1016/j.dt.2013.10.005.

    """

    density: float
    force: float
    burn_rate_coefficient: float
    pressure_exponent: float
    covolume: float
    adiabatic_index: float
    gas_molar_mass: float
    arch_thickness: float
    form_function: FormFunction

    @classmethod
    def from_impulse(
        cls,
        density: float,
        force: float,
        impulse: float,
        pressure_exponent: float,
        covolume: float,
        adiabatic_index: float,
        molar_mass: float,
        arch_thickness: float,
        form_function: FormFunction,
        n_intg: int,
        acc: float,
        load_density: float,
    ) -> Charge:
        """
        define a Charge from total impulse. Calls `Charge.I_k` within
        `ballistics.num.dekker` to numerically solve the burn-rate coefficient
        from the supplied geometry, impulse, and preessure exponent.

        Parameters
        ----------
        impulse: float
            total-pressure impulse until burnout, I_k, in Newton-second.

        acc, n_intg, load_density: int, float, float
            see documentation for `Charge.I_k`.
        """
        pass

    @cached_property
    def Z_k(self) -> float:
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

    def I_k(
        self,
        n_intg: int,
        acc: float,
        load_density: float = 0.2e3,
    ) -> float:
        """calculate the total impulse of this propellant, as defined by
        ```     t_k
        I_k =   ∫ P_(t) dt,  _k denotes end of combustion point.
                0
        ```
        Parameters
        ----------
        n_intg: int
            minimum number of steps taken from ignition to powder burnout.

        acc: float
            accuracy to which the ignition point is solved

        load_density: float
            the density to which the test bomb is loaded with propellant. The
            default value of 0.2 g/cc (200 kg/m^3) is a common choice of loading
            density for experimentation.

        Returns
        -------
        I_k: float
            propellant's total impulse.

        """

        """integrate backwards in time from burnout point to avoid asymptotic
        point at t = 0, then read-off the time and impulse-values as negatives.
        """
        n = 0
        delta_t = -MAX_DT
        rough_ttb = 0.0
        while n < n_intg:
            if rough_ttb < 0:
                delta_t = rough_ttb / n_intg
            n = 0

            bs_next = BombState(
                charge=self,
                load_density=load_density,
                time=0,
                burnup_fraction=self.Z_k,
                impulse=0,
            )
            while bs_next.pressure > 0:
                bs_next = self.propagate_rk4(bs_now := bs_next, delta_t)
                n += 1

            rough_ttb = bs_next.time

        tol_t = rough_ttb * acc

        def time_burnup(time: float) -> float:
            return self.propagate_rk4(
                bomb_state=bs_now, dt=time - bs_now.time
            ).burnup_fraction

        ignition_time = dekker(
            f=time_burnup, x_0=bs_now.time, x_1=bs_next.time, tol=tol_t
        )[0]
        bs_ignition = self.propagate_rk4(
            bomb_state=bs_now, dt=ignition_time - bs_now.time
        )

        return -bs_ignition.impulse

    def dt(self, bomb_state: BombState) -> BombDelta:
        P = bomb_state.pressure
        return BombDelta(d_time=1, d_burnup_fraction=self.dZdt(P), d_impulse=P)

    def propagate_rk4(self, bomb_state: BombState, dt: float) -> BombState:
        s_i = bomb_state.increment
        df = self.dt

        k1 = df(bomb_state)
        k2 = df(s_i(d=0.5 * k1 * dt, dt=0.5 * dt))
        k3 = df(s_i(d=0.5 * k2 * dt, dt=0.5 * dt))
        k4 = df(s_i(d=k3 * dt, dt=dt))
        return s_i(d=(k1 + k2 * 2 + k3 * 2 + k4) * dt / 6, dt=dt)


@dataclass(frozen=True)
class BombState:
    charge: Charge
    load_density: float

    time: float
    burnup_fraction: float  # Z
    impulse: float  # I_k

    def __getattr__(self, item):
        return getattr(self.charge, item)

    @cached_property
    def volume_burnup_fraction(self) -> float:
        return self.psi_c(max(self.burnup_fraction, 0))

    @cached_property
    def pressure(self) -> float:
        psi = self.volume_burnup_fraction
        return (self.force * psi) / (
            1 / self.load_density - (1 - psi) / self.density - self.covolume * psi
        )

    def increment(self, d: BombDelta, dt: float) -> BombState:
        return BombState(
            charge=self.charge,
            load_density=self.load_density,
            time=self.time + dt,
            burnup_fraction=self.burnup_fraction + d.d_burnup_fraction,
            impulse=self.impulse + d.d_impulse,
        )


@dataclass(frozen=True)
class BombDelta:
    d_time: float
    d_burnup_fraction: float
    d_impulse: float

    def __mul__(self, scalar: float) -> BombDelta:
        return BombDelta(
            d_time=self.d_time * scalar,
            d_burnup_fraction=self.d_burnup_fraction * scalar,
            d_impulse=self.d_impulse * scalar,
        )

    def __add__(self, other: BombDelta) -> BombDelta:
        return BombDelta(
            d_time=self.d_time + other.d_time,
            d_burnup_fraction=self.d_burnup_fraction + other.d_burnup_fraction,
            d_impulse=self.d_impulse + other.d_impulse,
        )

    def __rmul__(self, scalar: float) -> BombDelta:
        return self * scalar

    def __truediv__(self, scalar: float) -> BombDelta:
        return self * (1 / scalar)
