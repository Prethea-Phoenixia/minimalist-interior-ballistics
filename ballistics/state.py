from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, TYPE_CHECKING
from functools import cached_property
from .delta import Delta


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
    marker: str

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
        i_f, g_e = 0, 0
        for c, Z_c in zip(self.charges, self.burnup_fractions):
            psi_c = c.psi_c(min(Z_c, c.Z_k))
            i_f += c.incompressible_fraction(psi_c)
            g_e += c.gas_energy(psi_c)

        l, v, m = self.travel, self.velocity, self.shot_mass
        theta = self.average_adiabatic_index - 1
        l_psi = self.l_0 * (1 - i_f)
        P = (g_e - 0.5 * theta * self.phi * m * v**2) / (self.S * (l_psi + l))
        return P

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

    def increment(self, d: Delta, marker: str, dt=..., dl=..., dv=...) -> State:
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
