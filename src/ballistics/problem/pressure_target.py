from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state import State


class PressureTarget:

    BREECH = "breech_pressure"
    AVERAGE = "average_pressure"
    SHOT = "shot_pressure"

    def __init__(self, value: float, target: str):
        """
        do not call this constructor directly.
        """
        self.value = value
        self.target = target

    @classmethod
    def breech_pressure(cls, value: float):
        return cls(value, target=cls.BREECH)

    @classmethod
    def average_pressure(cls, value: float):
        return cls(value, target=cls.AVERAGE)

    @classmethod
    def shot_pressure(cls, value: float):
        return cls(value, target=cls.SHOT)

    def retrieve_from(self, state: State) -> float:
        return getattr(state, self.target)

    def describe(self) -> str:
        return self.target.replace("_", " ").upper() + f" {self.value * 1e-6:.3f} MPa"
