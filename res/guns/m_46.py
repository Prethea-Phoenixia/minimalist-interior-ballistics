from statistics import mean

from ballistics.form_function import FormFunction
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_sf3 import sf3

twentythree_one = FormFunction.single_perf(arch_width=mean((2.20, 2.35)), height=370)
m_46_full = KnownGunProblem(
    name="Type 1959 130mm Cannon (M-46) (WB005P HE-Frag, Full Charge)",
    description="Type 1959 130mm cannon is the designation for domestically produced \
variants of the Soviet 130mm towed field gun M1954 (M-46). The Full Variable charge \
is supplied with a main charge bag of 11kg, and a supplementary charge bag of 1.9kg. \
This case represents when both are left in. Nominal velocity is 930m/s. Peak pressure\
converted from copper crusher gauge, nominally 315,000 kgf/dm^2. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=12.9,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=59.52 * dm,
    propellant=sf3,
    form_function=twentythree_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(3370e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)

m_46_one = Gun(
    name="Type 1959 130mm Cannon (M-46) (WB005P HE-Frag, No.1 Charge)",
    description="Type 1959 130mm cannon is the designation for domestically produced \
variants of the Soviet 130mm towed field gun M1954 (M-46). The Full Variable cahrge is \
supplied with a main charge bag of 11kg, and a supplementary charge bag of 1.9kg. \
This case represents the supplementary charge bag taken out. Nominal velocity \
is 810m/s.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=11,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=59.52 * dm,
    charge=m_46_full.charge,
)

if __name__ == "__main__":
    from ballistics.state import StateList

    print(StateList.tabulate(m_46_full.to_travel(n_intg=10)))
    print(StateList.tabulate(m_46_one.to_travel(n_intg=10)))
