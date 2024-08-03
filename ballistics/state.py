from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, TYPE_CHECKING
from functools import cached_property
from . import Significance

if TYPE_CHECKING:
    from .gun import Gun


@dataclass(frozen=True)
class State:
    """class representing a particular point in the interior ballistic system
    of equations.
    """

    gun: Gun = field(repr=False)
    time: float
    travel: float
    velocity: float
    burnup_fractions: Tuple[float, ...]
    marker: Significance

    def __getattr__(self, item):
        return getattr(self.gun, item)

    def __lt__(self, other: State):
        return self.time < other.time

    @cached_property
    def volume_burnup_fractions(self) -> Tuple[float]:
        return tuple(
            c.psi_c(min(Z_c, c.Z_k))
            for c, Z_c in zip(self.charges, self.burnup_fractions)
        )

    @cached_property
    def average_pressure(self) -> float:
        """the length-averaged pressure in the equivalent gun, under the Lagrange
        gradient of 0-dimensional interior ballistics.

        Notes
        -----
        The equivalent gun is a is formed by stretching the chamber volume of the
        actual gun into a section such that the gun is of uniform cross section
        throughout. The error of this treatment is usually insignificant for the range
        of conditions encountered in conventional firearms (although it is of more
        concern in light-gas guns).
        """
        psi = self.volume_burnup_fractions
        l, v = self.travel, self.velocity
        l_psi = self.l_0 * (1 - self.incompressible_fraction(psi))

        return self.gas_energy(psi, v) / (self.S * (l_psi + l))

    @cached_property
    def shot_pressure(self) -> float:
        """the shot-base pressure in the equivalent gun. For more info refer to
        `average_pressure`.
        """
        return self.average_pressure / (
            1 + self.total_charge_mass / (3 * (1 + self.loss_fraction) * self.shot_mass)
        )

    @cached_property
    def breech_pressure(self) -> float:
        """the breech face pressure in the equivalent gun. For more info refer to
        `average_pressure`.
        """
        return self.shot_pressure * (
            1 + self.total_charge_mass / (2 * (1 + self.loss_fraction) * self.shot_mass)
        )

    def increment(
        self, d: Delta, marker: Significance, dt=..., dl=..., dv=...
    ) -> State:
        if dt != ...:
            dx, d_attr = dt, "time"
        elif dl != ...:
            dx, d_attr = dl, "travel"
        elif dv != ...:
            dx, d_attr = dv, "velocity"
        else:
            raise ValueError("at least one of `dv, dt, dl` must be specified.")

        attrs = {
            v_attr: getattr(self, v_attr)
            + (getattr(d, "d_" + v_attr) if d_attr != v_attr else dx)
            for v_attr in ("time", "travel", "velocity")
        }

        return State(
            gun=self.gun,
            **attrs,
            burnup_fractions=tuple(
                Z + dZ for Z, dZ in zip(self.burnup_fractions, d.d_burnup_fractions)
            ),
            marker=marker,
        )


@dataclass(frozen=True)
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
