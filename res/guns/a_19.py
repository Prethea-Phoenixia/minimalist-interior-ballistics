from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction
from ballistics.problem import (FixedChargeProblem, KnownGunProblem,
                                PressureTarget)
from misc import (L, dm, dm2, dm3_kg, format_compo_string, kg_dm3, kgf_dm2,
                  kgfdm_kg)

yf3 = Propellant(
    name="乙芳-3",
    description="2504 K\n\
《火炸药手册 (增订本）第二分册》(1981), 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string(
        {
            "Nitrocellulose": 0.625,
            "Diethylene Glycol Dinitrate": 0.295,
            "Dinitrotoluene": 0.04,
            "Ethyl/Methyl Centralite": 0.03,
            "Vaseline": 0.01,
        }
    ),
    density=1.6 * kg_dm3,
    force=986600 * kgfdm_kg,
    pressure_exponent=0.81,
    covolume=1.04117 * dm3_kg,
    adiabatic_index=1.2633,
)
seventeen_one = FormFunction.single_perf(arch_width=mean((1.70, 1.80)), height=225)
a_19 = KnownGunProblem(
    name="Type 1931/37 122mm Cannon (A-19) (WB013P HE-Frag)",
    description="Type 1931/1937 122mm cannon is the domestic designation for the \
Soviet 122mm corps gun M1931/1937 (A-19). Nominal velocity is 800m/s. Pressure \
values converted from copper crusher gauge values, nominally 275,000 kgf/dm^2. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.188 * dm2,
    shot_mass=25,
    charge_mass=6.847,
    chamber_volume=9.898 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.55 * dm,
    propellant=yf3,
    form_function=seventeen_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(2838e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)
if __name__ == "__main__":
    from ballistics.state import StateList

    print(StateList.tabulate(a_19.to_travel(n_intg=10)))
