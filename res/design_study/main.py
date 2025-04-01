import logging
from math import pi
from statistics import mean

from minimalist_interior_ballistics import Significance
from minimalist_interior_ballistics.charge import Charge, Propellant
from minimalist_interior_ballistics.form_function import FormFunction, MultiPerfShape
from minimalist_interior_ballistics.gun import Gun
from minimalist_interior_ballistics.problem import (
    FixedChargeProblem,
    FixedVolumeProblem,
    KnownGunProblem,
    PressureTarget,
)
from minimalist_interior_ballistics.state import StateList
from tabulate import tabulate

# from misc import L, dm, dm2, dm3_kg, kg_dm3, kgf_dm2, kgfdm_kg, mm


dm = 1e-1
dm2 = 1e-2
L = 1e-3
kg_dm3 = 1e3
dm3_kg = 1e-3
kgfdm_kg = 0.98
kgf_dm2 = 980
dm_s = 0.1
mm = 1e-3


NDT_3 = Propellant(
    name="НДТ-3",
    density=1.6 * kg_dm3,
    force=960e3,
    pressure_exponent=1,
    burn_rate_coefficient=5.61e-10,
    covolume=1.0e-3,
    adiabatic_index=1.2,
)

twentythree_one = FormFunction.single_perf(arch_width=2.3 * mm, height=370 * mm)

pressure_target = PressureTarget.breech_pressure(350e6)
velocity_target = 1024


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",  # [%(filename)s-%(funcName)s:%(lineno)d]",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="main.log",
    filemode="w+",
)


cals = (40, 50, 60, 70, 80)
cms = (20, 25, 30, 35)

charges = [[f"{velocity_target:.0f} m/s @ {pressure_target.describe()}", *(f"{cm} kg" for cm in cms)]]

for cal in cals:
    charge = [f"L/{cal}"]
    for cm in cms:
        fcp = FixedChargeProblem(
            name="Provisional 176mm",
            description="Triskelan",
            family="176mm",
            shot_mass=80,
            charge_mass=cm,
            cross_section=0.25 * pi * (176e-3) ** 2,
            propellant=NDT_3,
            form_function=twentythree_one,
            travel=176e-3 * cal,
        )

        try:
            low_gun, high_gun = fcp.solve_chamber_volume_at_pressure_for_velocity(
                pressure_target=pressure_target, velocity_target=velocity_target
            )

            entry = ""
            if low_gun:
                low_states = low_gun.to_travel()
                if low_states.has_state_with_marker(Significance.BURNOUT):
                    low_bop = f"{low_states.burnout_point / low_states.travel:.0%}"
                else:
                    low_bop = ">100%"

                entry += f"{low_gun.chamber_volume * 1e3:.1f} L ({low_bop})"

            entry += " "

            if high_gun:
                high_states = high_gun.to_travel()
                if high_states.has_state_with_marker(Significance.BURNOUT):
                    high_bop = f"{high_states.burnout_point / high_states.travel:.0%}"
                else:
                    high_bop = ">100%"

                entry += f"{high_gun.chamber_volume * 1e3:.1f} L ({high_bop})"

            charge.append(entry)  # and high_gun.delta < 700

        except ValueError:
            charge.append("----")

    # vels.append(vel)
    charges.append(charge)
# print(tabulate(vels, tablefmt="latex_booktabs", floatfmt=".1f"))

print(tabulate(charges, floatfmt=".1f"))
print(tabulate(charges, tablefmt="latex_booktabs", floatfmt=".1f"))
