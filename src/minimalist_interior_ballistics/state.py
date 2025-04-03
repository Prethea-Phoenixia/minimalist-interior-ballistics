from __future__ import annotations

import sys
from collections import UserList
from functools import cached_property
from math import inf
from typing import TYPE_CHECKING, Iterable, Optional

from attrs import field, frozen
from tabulate import tabulate

from . import Significance

if TYPE_CHECKING:
    from .gun import Gun


@frozen(kw_only=True)
class State:
    """class representing a particular point in the interior ballistic system
    of equations.
    """

    gun: Gun = field(repr=False)
    sv: StateVector
    marker: Significance
    is_started: bool = True

    def __lt__(self, other: State):
        # this enables sorting and bisect operation with array of `minimalist_interior_ballistics.state.State`.
        return self.time < other.time

    @cached_property
    def time(self) -> float:
        return self.sv.time

    @cached_property
    def travel(self) -> float:
        return self.sv.travel

    @cached_property
    def velocity(self) -> float:
        return self.sv.velocity

    @cached_property
    def burnup_fractions(self) -> tuple[float, ...]:
        return self.sv.burnup_fractions

    @staticmethod
    def remark(old_state: State, new_significance: Significance) -> State:
        return State(
            gun=old_state.gun,
            sv=StateVector(
                time=old_state.time,
                travel=old_state.travel,
                velocity=old_state.velocity,
                burnup_fractions=old_state.burnup_fractions,
            ),
            marker=new_significance,
        )

    @cached_property
    def volume_burnup_fractions(self) -> tuple[float, ...]:

        return tuple(
            charge.psi(max(min(burnup_fraction, charge.Z_k), 0))
            for charge, burnup_fraction in zip(self.gun.charges, self.burnup_fractions)
        )

    @cached_property
    def gross_volume_burnup_fraction(self) -> float:
        # mass weighted fraction of the above

        return (
            sum(m * psi for m, psi in zip(self.gun.charge_masses, self.volume_burnup_fractions))
            / self.gun.gross_charge_mass
        )

    @cached_property
    def average_pressure(self) -> float:
        """the length-averaged pressure in the equivalent gun, under the Lagrange
        gradient of 0-dimensional interior minimalist_interior_ballistics.

        Notes
        -----
        The equivalent gun is formed by stretching the chamber volume of the
        actual gun into a section such that the gun is of uniform cross-section
        throughout. The error of this treatment is usually insignificant for the range
        of conditions encountered in conventional firearms (although it is of more
        concern in light gas guns).
        """
        l, v = self.travel, self.velocity
        l_psi = self.gun.l_0 * (1 - self.gun.incompressible_fraction(self.volume_burnup_fractions))
        if l_psi <= 0:
            return inf
        else:
            return self.gun.gas_energy(psis=self.volume_burnup_fractions, v=v) / (self.gun.S * (l_psi + l))

    @cached_property
    def shot_pressure(self) -> float:
        """the shot-base pressure in the equivalent gun. For more info refer to
        `average_pressure`.
        """
        return self.average_pressure / (
            1 + self.gun.gross_charge_mass / (3 * self.gun.shot_mass * (1 + self.gun.loss_fraction))
        )

    @cached_property
    def breech_pressure(self) -> float:
        """the breech face pressure in the equivalent gun. For more info refer to
        `average_pressure`.
        """
        return self.shot_pressure * (
            1 + self.gun.gross_charge_mass / (2 * self.gun.shot_mass * (1 + self.gun.loss_fraction))
        )

    @cached_property
    def is_burnout(self) -> bool:
        return all(Z > charge.Z_k for charge, Z in zip(self.gun.charges, self.burnup_fractions))

    def increment_time(self, d: StateVector, dt: float, marker: Significance) -> State:
        return State(
            gun=self.gun,
            sv=StateVector(
                time=self.time + dt,
                travel=self.travel + d.travel,
                velocity=self.velocity + d.velocity,
                burnup_fractions=tuple(v + w for v, w in zip(self.burnup_fractions, d.burnup_fractions)),
            ),
            marker=marker,
            is_started=self.is_started,
        )

    def increment_travel(self, d: StateVector, dl: float, marker: Significance) -> State:
        return State(
            gun=self.gun,
            sv=StateVector(
                time=self.time + d.time,
                travel=self.travel + dl,
                velocity=self.velocity + d.velocity,
                burnup_fractions=tuple(v + w for v, w in zip(self.burnup_fractions, d.burnup_fractions)),
            ),
            marker=marker,
            is_started=self.is_started,
        )

    def increment_velocity(self, d: StateVector, dv: float, marker: Significance) -> State:
        return State(
            gun=self.gun,
            sv=StateVector(
                time=self.time + d.time,
                travel=self.travel + d.travel,
                velocity=self.velocity + dv,
                burnup_fractions=tuple(v + w for v, w in zip(self.burnup_fractions, d.burnup_fractions)),
            ),
            marker=marker,
            is_started=self.is_started,
        )


@frozen(kw_only=True)
class StateVector:
    time: float
    travel: float
    velocity: float
    burnup_fractions: tuple[float, ...]

    def __mul__(self, scalar: float) -> StateVector:
        return StateVector(
            time=self.time * scalar,
            travel=self.travel * scalar,
            velocity=self.velocity * scalar,
            burnup_fractions=tuple(burnup_fraction * scalar for burnup_fraction in self.burnup_fractions),
        )

    def __add__(self, other: StateVector) -> StateVector:
        return StateVector(
            time=self.time + other.time,
            travel=self.travel + other.travel,
            velocity=self.velocity + other.velocity,
            burnup_fractions=tuple(w + v for w, v in zip(self.burnup_fractions, other.burnup_fractions)),
        )

    def __rmul__(self, scalar: float) -> StateVector:
        return self * scalar

    def __truediv__(self, scalar: float) -> StateVector:
        return self * (1 / scalar)


# this is a limitation of pre- Python 3.9 style type annotations
if sys.version_info >= (3, 9):
    BaseList = UserList[State]
else:
    BaseList = UserList


class StateList(BaseList):
    def __init__(self, seq: Optional[Iterable[State]] = None) -> None:
        super().__init__(seq)

    def get_state_by_marker(self, significance: Significance) -> State:
        for s in self.data:
            if s.marker == significance:
                return s
        raise ValueError(f"StateList does not contain State with marker {significance}.")

    def has_state_with_marker(self, significance: Significance) -> bool:
        for s in self.data:
            if s.marker == significance:
                return True
        return False

    @property
    def muzzle_velocity(self) -> float:
        return self.get_state_by_marker(Significance.MUZZLE).velocity

    @property
    def travel(self) -> float:
        return self.get_state_by_marker(Significance.MUZZLE).travel

    @property
    def burnout_point(self) -> float:
        return self.get_state_by_marker(Significance.BURNOUT).travel

    @property
    def peak_shot_pressure(self) -> float:
        return self.get_state_by_marker(Significance.PEAK_PRESSURE).shot_pressure

    @property
    def peak_average_pressure(self) -> float:
        return self.get_state_by_marker(Significance.PEAK_PRESSURE).average_pressure

    def tabulate(
        self,
        *args,
        headers: Iterable[str] = (
            "significance",
            "time\nms",
            "travel\nm",
            "velocity\nm/s",
            "breech\npressure\nMPa",
            "average\npressure\nMPa",
            "shot\npressure\nMPa",
            "volume\nburnup\nfraction\n[charge 1]",
            "\n\n\n[charge 2]",
            "\n\n\n[charge 3]",
        ),
        floatfmt: str = ".4g",
        concise: bool = True,
        **kwargs,
    ) -> str:
        """
        Generates a plain, tabulated view of data for a list of
        `State` objects.

        Parameters
        ----------
        states: list of `ballistics.state.State`
            the list of `minimalist_interior_ballistics.state.State` to be pretty-printed.
        headers: tuple[str]
            argument passed to `tabulate.tabulate()` to generate a header for the
            table.
        *args, **kwargs:
            other positional and named arguments to be passed to `tabulate.tabulate()`,
            after the aforementioned once, respectively.

        Returns
        -------
        str
            generated using `tabulate.tabulate()`.

        Notes
        -----
        see documentation for [tabulate.tabulate](https://pypi.org/project/tabulate/)
        for information on additional arguments.
        """
        return tabulate(
            [
                (
                    state.marker.value,
                    state.time * 1e3,
                    state.travel,
                    state.velocity,
                    state.breech_pressure * 1e-6,
                    state.average_pressure * 1e-6,
                    state.shot_pressure * 1e-6,
                    *state.volume_burnup_fractions,
                )
                for state in self
                if ((concise and state.marker != Significance.STEP) or (not concise))
            ],
            *args,
            **{**{"headers": headers, "floatfmt": floatfmt}, **kwargs},  # feeds additional arguments
        )
