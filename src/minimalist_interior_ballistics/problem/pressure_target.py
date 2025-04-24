from __future__ import annotations

from attrs import field, frozen
from ..state import State


def _check_target(instance, attribute, value):
    if value not in (instance.BREECH, instance.AVERAGE, instance.SHOT):
        raise ValueError("`target` must be one of PressureTarget.BREECH, .AVERAGE, or .SHOT")


@frozen()
class PressureTarget:
    """
    class representing pressure target, encompassing both the numeric pressure value, and
    the location it is measured/specified as.

    Use of one of the three class methods:
    `PressureTarget.breech_pressure`, `PressureTarget.average_pressure`,
    `PressureTarget.shot_pressure`, is strongly advised.
    """

    value: float
    target: str = field(validator=_check_target)

    def __mul__(self, other: float) -> PressureTarget:
        if isinstance(other, float):
            return PressureTarget(value=self.value * other, target=self.target)
        else:
            raise ValueError(f"instance of PressureTarget cannot be multiplied with type {type(other)}")

    def __rmul__(self, other: float) -> PressureTarget:
        return self * other

    def __truediv__(self, other) -> PressureTarget:
        return self * (1 / other)

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
