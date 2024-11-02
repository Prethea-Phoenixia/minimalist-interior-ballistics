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
This case represents when firing the charge as issued. Nominal velocity is 930m/s. \
Nominal pressure is 3150 kgf/cm^2 in copper crusher gauge, converts to 3370 kgf/cm^2 \
actual. \n\
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
    pressure_target=PressureTarget.average_pressure(3370e2 * kgf_dm2),
)

m_46_one = Gun(
    name="Type 1959 130mm Cannon (M-46) (WB005P HE-Frag, No.1 Charge)",
    description="Type 1959 130mm cannon is the designation for domestically produced \
variants of the Soviet 130mm towed field gun M1954 (M-46). The Full Variable cahrge is \
supplied with a main charge bag of 11kg, and a supplementary charge bag of 1.9kg. \
This case represents the supplementary charge bag taken out. Nominal velocity \
is 810m/s. \n\
This entry adopts the same properties of charge from the preceeding entry, with a reduced \
charge mass. Further, a minor (<3%) reduction of charge mass from 11 to 10.787 \
kg is adopted to conform with the tabulated performance. This is probably within the range \
of variation allowed for in charge manufacturing, given Serbian sources lists a charge load \
of 12.6 kg and 10.5 kg, respectively, for the same charge design. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=10.787,
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
