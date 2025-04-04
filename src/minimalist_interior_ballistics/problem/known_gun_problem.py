from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import frozen
from ..gun import Gun
from .base_problem import BaseProblem, accepts_reduced_burnrates, accepts_charge_masses
from .pressure_target import PressureTarget

if TYPE_CHECKING:
    # these are required for pdoc to locate the references
    # noinspection PyUnresolvedReferences
    from ..charge import Propellant

    # noinspection PyUnresolvedReferences
    from ..form_function import FormFunction


@frozen(kw_only=True)
class KnownGunProblem(BaseProblem):
    chamber_volume: float
    charge_mass: Optional[float] = None
    charge_masses: list[float] | tuple[float, ...] = tuple()

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
            acc=base_problem.acc,
            n_intg=base_problem.n_intg,
        )

    @accepts_reduced_burnrates
    def get_gun(
        self,
        reduced_burnrates: tuple[float, ...],
        **kwargs,
    ) -> Gun:

        return super().get_gun(
            charge_mass=self.charge_mass,
            charge_masses=self.charge_masses,
            chamber_volume=self.chamber_volume,
            reduced_burnrates=reduced_burnrates,
        )

    def get_gun_at_pressure(
        self,
        pressure_target: PressureTarget,
        reduced_burnrate_ratios: list[float] | tuple[float, ...] = tuple([1.0]),
        **kwargs,
    ) -> Gun:

        return super().get_gun_at_pressure(
            charge_mass=self.charge_mass,
            charge_masses=self.charge_masses,
            chamber_volume=self.chamber_volume,
            reduced_burnrate_ratios=reduced_burnrate_ratios,
            pressure_target=pressure_target,
        )
