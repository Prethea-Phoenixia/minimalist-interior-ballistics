from statistics import mean

from ballistics.form_function import FormFunction
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_9_7 import nine_seven, sb_9_7
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


m_46_four = KnownGunProblem(
    name="Type 1959 130mm Cannon (M-46) (WB005P HE-Frag, No.4 Charge)",
    description="Type 1959 130mm cannon is the designation for domestically produced \
variants of the Soviet 130mm towed field gun M1954 (M-46). The Reduced Variable charge \
is supplied with a 0.7 kg bundle of 7/1 propellant, and 5.8 kg of 9/7 propellant. \
This case represents firing with two balanced increments removed, with 3.22 kg of 9/7. \
Nominal velocity is 525m/s. Nominal pressure is >=1100 kgf/cm^2 in copper crusher gauge. \n\
Due to limitations of this framework, the 7/1 charge has been treated as equivalent weight \
in 9/7 for this entry. A pressure of 1137 kgf/cm^2 has been adopted, taking conformity \
of charge 2, 3 and 4 into account.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=3.92,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=59.52 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(1137e2 * kgf_dm2),
)


m_46_three = Gun(
    name="Type 1959 130mm Cannon (M-46) (WB005P HE-Frag, No.3 Charge)",
    description="Type 1959 130mm cannon is the designation for domestically produced \
variants of the Soviet 130mm towed field gun M1954 (M-46). The Reduced Variable charge \
is supplied with a 0.7 kg bundle of 7/1 propellant, and 5.8 kg of 9/7 propellant. \
This case represents firing with one balanced increments removed, with 4.52 kg of 9/7. \
Nominal velocity is 620 m/s. \n\
Due to limitations of this framework, the 7/1 charge has been treated as equivalent weight \
in 9/7 for this entry. As well, the charge characteristics of the No.4 charge has been \
used, with an increase in charge weight. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=5.22,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=59.52 * dm,
    charge=m_46_four.charge,
)

m_46_two = Gun(
    name="Type 1959 130mm Cannon (M-46) (WB005P HE-Frag, No.2 Charge)",
    description="Type 1959 130mm cannon is the designation for domestically produced \
variants of the Soviet 130mm towed field gun M1954 (M-46). The Reduced Variable charge \
is supplied with a 0.7 kg bundle of 7/1 propellant, and 5.8 kg of 9/7 propellant. \
This case represents firing the charge as issued. Nominal velocity is 705 m/s. \n\
Due to limitations of this framework, the 7/1 charge has been treated as equivalent weight \
in 9/7 for this entry. As well, the charge characteristics of the No.4 charge has been \
used, with an increase in charge weight.  \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=6.5,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=59.52 * dm,
    charge=m_46_four.charge,
)

all_guns = [m_46_full, m_46_one, m_46_two, m_46_three, m_46_four]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
