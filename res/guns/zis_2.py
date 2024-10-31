from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import (L, dm, dm2, dm3_kg, format_compo_string, kg_dm3, kgf_dm2,
                  kgfdm_kg)

sb = Propellant(
    name="Single Base",
    description="2796 K, Nitrated to 204-207.5 mL/g\n《火炸药手册 (增订本）第二分册》(1981)\
, 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
    density=1.6 * kg_dm3,
    force=1011300 * kgfdm_kg,
    # force=950000 * kgfdm_kg,
    pressure_exponent=0.84,
    covolume=0.95576 * dm3_kg,
    adiabatic_index=1.2391,
)

fourteen_seven = FormFunction.multi_perf(
    arch_width=mean((1.20, 1.55)),
    perforation_diameter=mean((0.7, 0.8)),
    height=mean((16, 18)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)
zis_2 = KnownGunProblem(
    name="Type 1955 57mm Cannon (WB009 HE-Frag) (ZiS-2)",
    description="Type 1955 57mm Cannon is the domestic designation for the Soviet 57mm \
anti-tank gun M1943 (ZiS-2, GRAU index 52-P-271).\n\
Note that commonly quoted value for this gun and shell combination is ~700m/s. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.2663 * dm2,
    shot_mass=3.75,
    charge_mass=0.98,
    chamber_volume=1.875 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=35.66 * dm,
    propellant=sb,
    form_function=fourteen_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(2000e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)

if __name__ == "__main__":
    from ballistics.state import StateList

    print(fourteen_seven)
    print(zis_2)
    print(StateList.tabulate(zis_2.to_travel(n_intg=10)))
