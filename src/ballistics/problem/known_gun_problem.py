from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import frozen
from ballistics import DEFAULT_ACC, DEFAULT_STEPS
from ballistics.problem.base_problem import BaseProblem

if TYPE_CHECKING:
    from ballistics.gun import Gun
    from ballistics.problem.pressure_target import PressureTarget


@frozen(kw_only=True)
class KnownGunProblem(BaseProblem):
    chamber_volume: float
    charge_mass: Optional[float] = None
    charge_masses: list[float] | tuple[float, ...] = tuple()

    def __attrs_post_init__(self):
        super().__attrs_post_init__()  # todo: test if this is needed.
        if self.charge_mass:
            object.__setattr__(self, "charge_masses", tuple([self.charge_mass]))

        if self.charge_masses:
            if len(self.charge_masses) != len(self.propellants):
                raise ValueError("charge_masses must have the same dimension as self.propellants and form_functions")
        else:
            raise ValueError("invalid parameters")

    @classmethod
    def from_base_problem(
        cls,
        base_problem: BaseProblem,
        chamber_volume: float,
        charge_mass: Optional[float] = None,
        charge_masses: list[float] | tuple[float, ...] = tuple(),
    ) -> KnownGunProblem:
        return cls(
            name=base_problem.name,
            description=base_problem.description,
            family=base_problem.family,
            propellant=base_problem.propellant,
            propellants=base_problem.propellants,
            form_function=base_problem.form_function,
            form_functions=base_problem.form_functions,
            cross_section=base_problem.cross_section,
            shot_mass=base_problem.shot_mass,
            travel=base_problem.travel,
            loss_fraction=base_problem.loss_fraction,
            start_pressure=base_problem.start_pressure,
            chamber_volume=chamber_volume,
            charge_mass=charge_mass,
            charge_masses=charge_masses,
        )

    def get_gun(
        self,
        *,
        reduced_burnrate: Optional[float] = None,
        reduced_burnrates: Optional[list[float] | tuple[float, ...]] = None,
        **kwargs,
    ) -> Gun:

        if reduced_burnrate:
            reduced_burnrates = tuple([reduced_burnrate])

        if reduced_burnrates:
            if len(reduced_burnrates) != len(self.propellants):
                raise ValueError(
                    "reduced_burnrates must have the same dimension as self.propellants, charge_masses and form_functions"
                )
        else:
            raise ValueError("invalid parameters.")

        return super().get_gun(
            charge_masses=self.charge_masses, chamber_volume=self.chamber_volume, reduced_burnrates=reduced_burnrates
        )

    def get_gun_at_pressure(
        self,
        pressure_target: PressureTarget,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        *,
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
        **kwargs,
    ) -> Gun:

        return super().get_gun_at_pressure(
            charge_masses=self.charge_masses,
            chamber_volume=self.chamber_volume,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            pressure_target=pressure_target,
            n_intg=n_intg,
            acc=acc,
        )
