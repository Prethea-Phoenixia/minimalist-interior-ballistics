from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


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
