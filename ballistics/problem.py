from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Tuple

from . import Significance
from .charge import Charge
from .gun import Gun

if TYPE_CHECKING:
    from .state import State
    from .form_function import FormFunction


class Target(Enum):
    # BREECH = State.breech_pressure.__name__
    # AVERAGE = State.average_pressure.__name__
    # SHOT = State.shot_pressure.__name__
    BREECH = "breech_pressure"
    AVERAGE = "average_pressure"
    SHOT = "shot_pressure"


@dataclass(frozen=True)
class MatchingProblem:
    """
    Given known gun and charge loading parameters, deduce the (additional) charge
    that is required to *match* the performance, in terms of peak pressure and
    shot velocity.
    """

    caliber: float
    shot_mass: float
    chamber_volume: float
    travel: float
    loss_fraction: float
    start_pressure: float
    ignition_pressure: float

    density: float
    force: float
    pressure_exponent: float
    covolume: float
    adiabatic_index: float
    gas_molar_mass: float
    form_function: FormFunction

    known_charge_loads: Dict[Charge, float] = field(default_factory=dict)

    def solve(
        self,
        velocity: float,
        pressure: float,
        target: Target,
        n_intg: int,
        acc: float,
    ) -> Gun:

        def propose(
            proposed_mass: float, proposed_reduced_burnrate: float
        ) -> Tuple[Gun, Charge]:
            gun = Gun(
                caliber=self.caliber,
                shot_mass=self.shot_mass,
                chamber_volume=self.chamber_volume,
                loss_fraction=self.loss_fraction,
                start_pressure=self.start_pressure,
                ignition_pressure=self.ignition_pressure,
            )

            for charge, mass in self.known_charge_loads.items():
                gun.add_charge(charge=charge, mass=mass)

            charge = Charge(
                density=self.density,
                force=self.force,
                pressure_exponent=self.pressure_exponent,
                covolume=self.covolume,
                adiabatic_index=self.adiabatic_index,
                reduced_burnrate=proposed_reduced_burnrate,
                gas_molar_mass=self.gas_molar_mass,
                form_function=self.form_function,
            )
            gun.add_charge(charge=charge, mass=proposed_mass)

            return gun, charge

        def f(proposed_mass: float, proposed_reduced_burnrate: float):
            gun, _ = propose(
                proposed_mass=proposed_mass,
                proposed_reduced_burnrate=proposed_reduced_burnrate,
            )

            states = gun.to_travel(travel=self.travel, n_intg=n_intg, acc=acc)

            p_max, v_muzzle = 0.0, 0.0
            for state in states:
                if state.marker == Significance.PEAK_PRESSURE:
                    p_max = getattr(state, target.value)
                if state.marker == Significance.MUZZLE:
                    v_muzzle = state.velocity

            return p_max, v_muzzle

        # iteration loop

        mass, reduced_burnrate = 1.0, 1

        for _ in range(5):
            p_act, v_act = f(mass, reduced_burnrate)

            mass *= (v_act / velocity) ** 1.5
            reduced_burnrate *= (p_act / pressure) ** 0.45
            print(mass, reduced_burnrate)

        print(mass, reduced_burnrate)
        print(f(mass, reduced_burnrate))
