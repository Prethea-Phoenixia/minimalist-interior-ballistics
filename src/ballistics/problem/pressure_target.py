from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import field, frozen

from ..state import State


@frozen()
class PressureTarget:
    """
    class representing pressure target, encompassing both the numeric pressure value, as
    well as the location it is measured/specified as.

    Use of one of the three classmethods:
    `PressureTarget.breech_pressure`, `PressureTarget.average_pressure`,
    `PressureTarget.shot_pressure`, instead of manually specifying the various pressure points
    is strongly advised.
    """

    value: float
    target: str = field(kw_only=True)

    @target.validator
    def _check_target(self, attribute, value):
        if value not in (self.BREECH, self.AVERAGE, self.SHOT):
            raise ValueError("`target` must be one of PressureTarget.BREECH, .AVERAGE, or .SHOT")

    # these are dependent on the State class implementing fields with these exact names.
    BREECH = State.breech_pressure.__name__
    AVERAGE = State.average_pressure.__name__
    SHOT = State.shot_pressure.__name__

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

    def get_difference(self, state: State) -> float:
        """equivalent to `pt.retrieve_from(state) - pt.value`"""
        return getattr(state, self.target) - self.value

    def describe(self) -> str:
        return self.target.replace("_", " ").lower() + f" {self.value * 1e-6:.3f} MPa"
