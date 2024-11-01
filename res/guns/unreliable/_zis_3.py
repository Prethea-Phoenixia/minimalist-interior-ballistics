from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import (L, dm, dm2, dm3_kg, format_compo_string, kg_dm3, kgf_dm2,
                  kgfdm_kg)

sb = Propellant(
    name="Single Base",
    description="2811 K, Nitrated to 204-207.5 mL/g\n《火炸药手册 (增订本）第二分册》(1981)\
, 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
    density=1.6 * kg_dm3,
    force=1012200 * kgfdm_kg,
    pressure_exponent=0.83,
    covolume=0.95160 * dm3_kg,
    adiabatic_index=1.2381,
)
nine_seven = FormFunction.multi_perf(
    arch_width=mean((0.95, 1.10)),
    perforation_diameter=mean((0.40, 0.60)),
    height=mean((11.5, 12.6)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)


zis_3 = KnownGunProblem(
    name="Type 1954 76mm Cannon (WB022P HE-Frag) (ZiS-3)",
    description="Type 1954 76mm Cannon is the domestic designation for the Soviet 76.2mm \
divisional gun M1942 (ZiS-3, GRAU index 52-P-354U).\nReference:\n 《火炮内弹道计算手册》(1987)\
\n 《火炸药手册 (增订本）第二分册》(1981).",
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

    print(nine_seven)
    print(nine_seven.labda_s, nine_seven.chi_s)

    print(StateList.tabulate(zis_3.to_travel(n_intg=10)))
