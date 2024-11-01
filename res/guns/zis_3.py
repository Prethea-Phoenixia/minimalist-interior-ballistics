from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import (L, dm, dm2, dm3_kg, format_compo_string, kg_dm3, kgf_dm2,
                  kgfdm_kg)
from prop_9_7 import nine_seven, sb

zis_3 = KnownGunProblem(
    name="Type 1954 76mm Cannon (ZiS-3) (WB022P HE-Frag)",
    description="Type 1954 76mm Cannon is the domestic designation for the Soviet 76.2mm \
divisional gun M1942 (ZiS-3, GRAU index 52-P-354U). Nomianl velocity is 680 m/s. Pressure \
has been converted from copper crusher gauge values, at 238,000 kgf/dm^2.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.469 * dm2,
    shot_mass=6.2,
    charge_mass=1.08,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=26.87 * dm,
    propellant=sb,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(2617e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)
if __name__ == "__main__":
    from ballistics.state import StateList

    print(StateList.tabulate(zis_3.to_travel(n_intg=10)))
