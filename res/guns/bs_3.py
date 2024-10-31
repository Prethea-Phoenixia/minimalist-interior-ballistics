from ballistics.charge import Propellant
from ballistics.form_function import FormFunction
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import (L, dm, dm2, dm3_kg, format_compo_string, kg_dm3, kgf_dm2,
                  kgfdm_kg)

sf3 = Propellant(
    name="双芳-3",
    description="2580 K\n《火炸药手册 (增订本）第二分册》(1981)\
, 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string(
        {
            "Nitrocellulose": 0.56,
            "Nitroglycerin": 0.265,
            "Dinitrotoluene": 0.09,
            "Dibutyl phthalat": 0.045,
            "Ethyl/Methyl Centralite": 0.03,
            "Vaseline": 0.01,
        }
    ),
    density=1.56 * kg_dm3,
    force=1001400 * kgfdm_kg,
    pressure_exponent=0.81,
    covolume=1.02561 * dm3_kg,
    adiabatic_index=1.2663,
)
eighteen_one = FormFunction.single_perf(arch_width=0.85 * 2, height=260)
bs_3 = KnownGunProblem(
    name="Type 1944 100mm Cannon (WB004P HE-Frag) (BS-3)",
    description="Type 1944 100mm cannon is the domestic designation for the Soviet 100mm \
field gun M1944 (BS-3).\nReference:\n 《火炮内弹道计算手册》(1987)\n 《火炸药手册 (增订本）第二分册》\
(1981).",
    cross_section=0.818 * dm2,
    shot_mass=15.6,
    charge_mass=5.6,
    chamber_volume=7.9 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.38 * dm,
    propellant=sf3,
    form_function=eighteen_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(3141e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)


if __name__ == "__main__":
    from ballistics.state import StateList

    print(StateList.tabulate(bs_3.to_travel(n_intg=10)))
