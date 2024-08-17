from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .charge import Charge


@dataclass(frozen=True)
class BombState:
    """
    class describing the state of a ballistic bomb.
    """

    charge: Charge
    load_density: float
    ignition_pressure: float

    time: float
    burnup_fraction: float  # Z
    areal_impulse: float

    def __getattr__(self, item):
        return getattr(self.charge, item)

    @cached_property
    def volume_burnup_fraction(self) -> float:
        return self.psi_c(max(min(self.burnup_fraction, self.Z_k), 0))

    @cached_property
    def pressure(self) -> float:
        psi = self.volume_burnup_fraction
        return max(
            (
                self.force * psi
                + (self.load_density - 1 / self.density) * self.ignition_pressure
            )
            / (1 / self.load_density - (1 - psi) / self.density - self.covolume * psi),
            0,
        )

    def increment(self, d: BombDelta, dt: float) -> BombState:
        return BombState(
            charge=self.charge,
            load_density=self.load_density,
            ignition_pressure=self.ignition_pressure,
            time=self.time + dt,
            burnup_fraction=self.burnup_fraction + d.d_burnup_fraction,
            areal_impulse=self.areal_impulse + d.d_areal_impulse,
        )


@dataclass(frozen=True)
class BombDelta:

    d_time: float
    d_burnup_fraction: float
    d_areal_impulse: float

    def __mul__(self, scalar: float) -> BombDelta:
        return BombDelta(
            d_time=self.d_time * scalar,
            d_burnup_fraction=self.d_burnup_fraction * scalar,
            d_areal_impulse=self.d_areal_impulse * scalar,
        )

    def __add__(self, other: BombDelta) -> BombDelta:
        return BombDelta(
            d_time=self.d_time + other.d_time,
            d_burnup_fraction=self.d_burnup_fraction + other.d_burnup_fraction,
            d_areal_impulse=self.d_areal_impulse + other.d_areal_impulse,
        )

    def __rmul__(self, scalar: float) -> BombDelta:
        return self * scalar

    def __truediv__(self, scalar: float) -> BombDelta:
        return self * (1 / scalar)
