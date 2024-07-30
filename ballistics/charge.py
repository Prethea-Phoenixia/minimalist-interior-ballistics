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
    """class that represent individual charges as standalone designs."""

    density: float
    force: float
    burn_rate_coefficient: float
    pressure_exponent: float
    covolume: float
    adiabatic_index: float
    gas_molar_mass: float
    arch_thickness: float

    form_function: FormFunction

    @cached_property
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

    def I_k(
        self,
        n_intg: int = 10,
        acc: float = 1e-3,
        load_density: float = 0.2e3,
    ):
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
            default value of 0.2 g/cc

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

    def propagate_rk4(self, bomb_state: BombState, dt=float) -> BombState:
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

    def increment(self, d: BombDelta, dt=float) -> BombState:
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
