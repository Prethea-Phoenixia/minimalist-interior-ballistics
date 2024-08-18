from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Tuple

from . import (DEFAULT_GUN_IGNITION_PRESSURE, DEFAULT_GUN_START_PRESSURE,
               DFEAULT_GUN_LOSS_FRACTION, Significance)
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

    density: float
    force: float
    pressure_exponent: float
    covolume: float
    adiabatic_index: float
    gas_molar_mass: float
    form_function: FormFunction

    caliber: float
    shot_mass: float
    chamber_volume: float
    travel: float
    loss_fraction: float = DFEAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE
    ignition_pressure: float = DEFAULT_GUN_IGNITION_PRESSURE

    known_charge_loads: Dict[Charge, float] = field(default_factory=dict)

    def solve(
        self,
        velocity: float,
        pressure: float,
        target: Target,
        n_intg: int,
        acc: float,
    ) -> Gun:

        def propose(mass: float, reduced_burnrate: float) -> Tuple[Gun, Charge]:
            gun = Gun(
                caliber=self.caliber,
                shot_mass=self.shot_mass,
                chamber_volume=self.chamber_volume,
                loss_fraction=self.loss_fraction,
                start_pressure=self.start_pressure,
                ignition_pressure=self.ignition_pressure,
            )

            charge = Charge(
                density=self.density,
                force=self.force,
                pressure_exponent=self.pressure_exponent,
                covolume=self.covolume,
                adiabatic_index=self.adiabatic_index,
                reduced_burnrate=reduced_burnrate,
                gas_molar_mass=self.gas_molar_mass,
                form_function=self.form_function,
            )
            gun.add_charge(charge=charge, mass=mass)

            for charge, mass in self.known_charge_loads.items():
                gun.add_charge(charge=charge, mass=mass)

            return gun, charge

        def get_pv(mass: float, reduced_burnrate: float):
            gun, _ = propose(
                mass=mass,
                reduced_burnrate=reduced_burnrate,
            )

            states = gun.to_travel(travel=self.travel, n_intg=n_intg, acc=acc)

            print(Gun.prettyprint(states))

            p_max, v_muzzle = 0.0, 0.0
            for state in states:
                if state.marker == Significance.PEAK_PRESSURE:
                    p_max = getattr(state, target.value)
                if state.marker == Significance.MUZZLE:
                    v_muzzle = state.velocity

            return p_max, v_muzzle

        p, v = get_pv(mass=1, reduced_burnrate=0.00001)
        print(p / 1e6, v)
