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
    time: float
    travel: float
    velocity: float
    burnup_fraction: float
    marker: Significance
    is_started: bool = True

    def __lt__(self, other: State):
        # this enables sorting and bisect operation with array of `ballistics.state.State`.
        return self.time < other.time

    @staticmethod
    def remark(old_state: State, new_significance: Significance) -> State:
        return State(
            gun=old_state.gun,
            time=old_state.time,
            travel=old_state.travel,
            velocity=old_state.velocity,
            burnup_fraction=old_state.burnup_fraction,
            marker=new_significance,
        )

    @cached_property
    def volume_burnup_fraction(self) -> float:
        return self.gun.charge.psi(max(min(self.burnup_fraction, self.gun.charge.Z_k), 0))

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
        l, v = self.travel, self.velocity
        l_psi = self.gun.l_0 * (1 - self.gun.incompressible_fraction(self.volume_burnup_fraction))
        if l_psi <= 0:
            return inf
        else:
            return self.gun.gas_energy(psi=self.volume_burnup_fraction, v=v) / (
                self.gun.S * (l_psi + l)
            )

    @cached_property
    def shot_pressure(self) -> float:
        """the shot-base pressure in the equivalent gun. For more info refer to
        `average_pressure`.
        """
        return self.average_pressure / (
            (1 + self.gun.loss_fraction) + self.gun.charge_mass / (3 * self.gun.shot_mass)
        )

    @cached_property
    def breech_pressure(self) -> float:
        """the breech face pressure in the equivalent gun. For more info refer to
        `average_pressure`.
        """
        return self.shot_pressure * (
            (1 + self.gun.loss_fraction) + self.gun.charge_mass / (2 * self.gun.shot_mass)
        )

    def increment(self, d: Delta, marker: Significance, dt=..., dl=..., dv=...) -> State:
        if dt != ...:
            dx, d_attr = dt, "time"
        elif dl != ...:
            dx, d_attr = dl, "travel"
        elif dv != ...:
            dx, d_attr = dv, "velocity"
        else:
            raise ValueError("at least one of `dv, dt, dl` must be specified.")

        attrs = {
            v_attr: getattr(self, v_attr) + (getattr(d, "d_" + v_attr) if d_attr != v_attr else dx)
            for v_attr in ("time", "travel", "velocity", "burnup_fraction")
        }

        return State(
            gun=self.gun,
            **attrs,
            marker=marker,
            is_started=self.is_started,
        )


@frozen(kw_only=True)
class Delta:
    d_time: float
    d_travel: float
    d_velocity: float
    d_burnup_fraction: float

    def __mul__(self, scalar: float) -> Delta:
        return Delta(
            d_time=self.d_time * scalar,
            d_travel=self.d_travel * scalar,
            d_velocity=self.d_velocity * scalar,
            d_burnup_fraction=self.d_burnup_fraction * scalar,
        )

    def __add__(self, other: Delta) -> Delta:
        return Delta(
            d_time=self.d_time + other.d_time,
            d_travel=self.d_travel + other.d_travel,
            d_velocity=self.d_velocity + other.d_velocity,
            d_burnup_fraction=self.d_burnup_fraction + other.d_burnup_fraction,
        )

    def __rmul__(self, scalar: float) -> Delta:
        return self * scalar

    def __truediv__(self, scalar: float) -> Delta:
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

    def tabulate(
        self,
        *args,
        headers=(
            "significance",
            "time\nms",
            "travel\nm",
            "velocity\nm/s",
            "breech\npressure\nMPa",
            "average\npressure\nMPa",
            "shot\npressure\nMPa",
            "volume\nburnup\nfraction",
        ),
        **kwargs,
    ) -> str:
        """
        Generates a plain, tabulated view of data for a list of
        `State` objects.

        Parameters
        ----------
        states: list of `ballistics.state.State`
            the list of `ballistics.state.State` to be pretty-printed.
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
                    state.volume_burnup_fraction,
                )
                for state in self
            ],
            *args,
            **{**{"headers": headers}, **kwargs},  # feeds additional arguments
        )