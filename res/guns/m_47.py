from statistics import mean

from ballistics.form_function import FormFunction
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_4_1 import four_one, sb_4_1
from prop_sf3 import sf3

nineteen_one = FormFunction.single_perf(arch_width=mean((1.90, 1.95)), height=320)
m_47_full = KnownGunProblem(
    name="Type 1959 152mm Cannon (M-47) (WB008P HE-Frag, Full Charge)",
    description="Type 1959 152mm cannon is the designation for domestically produced \
variants of the Soviet 152mm towed field gun M1954 (M-47). The Full Variable charge is \
made up of various charge bags that adds up to 8.45kg. Further supplementary charge bags \
bring the full charge to 10.67 kg. Nominal velocity is 770 m/s. Nominal pressure is 2350 \
kgf/cm^2, converts to 2570 kgf/cm^2 actual.\n\
For this entry, a value of 2485 kgf/cm^2 has been adopted, which allows both this and \
the first reduced charge to better conform to nominal performance levels.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.876 * dm2,
    shot_mass=43.56,
    charge_mass=10.67,
    chamber_volume=17.27 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=55.77 * dm,
    propellant=sf3,
    form_function=nineteen_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(2485e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)

m_47_one = Gun(
    name="Type 1959 152mm Cannon (M-47) (WB008P HE-Frag, No.1 Charge)",
    description="Type 1959 152mm cannon is the designation for domestically produced \
variants of the Soviet 152mm towed field gun M1954 (M-47). The Full Variable charge is \
made up of various charge bags that adds up to 8.45kg. Further supplementary charge bags \
bring the full charge to 10.67 kg. Nominal velocity is 635 m/s.\n\
This entry adopts the same properties of charge from the preceeding entry, with a reduced \
charge mass. The calculated performance conforms to nominal values well.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.876 * dm2,
    shot_mass=43.56,
    charge_mass=8.45,
    chamber_volume=19.25 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=55.77 * dm,
    charge=m_47_full.charge,
)


m_47_two = KnownGunProblem(
    name="Type 1959 152mm Cannon (M-47) (WB008P HE-Frag, No.2 Charge)",
    description="Type 1959 152mm cannon is the designation for domestically produced \
variants of the Soviet 152mm towed field gun M1954 (M-47). The Reduced Variable charge is \
of bundle-and-loose-grain construction, with 0.25kg of 12/1 for the central bundle, and \
3.465 kg of loose 4/1 grains in charge bags. Nominal velocity is 500 m/s. Nominal pressure \
is <=2350 kgf/cm^2 from copper crusher gauge.\n\
For this entry, the 12/1 grains have been treated as equivalent mass in 4/1. \
In accordance, a pressure of 1550 kgf/cm^2 has been adopted, which allows both \
this and the third reduced charge to conform to nominal performance levels. \
The match is not unreasonable. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.876 * dm2,
    shot_mass=43.56,
    charge_mass=3.715,
    chamber_volume=17.27 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=55.77 * dm,
    propellant=sb_4_1,
    form_function=four_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(1550e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)

m_47_three = Gun(
    name="Type 1959 152mm Cannon (M-47) (WB008P HE-Frag, No.3 Charge)",
    description="Type 1959 152mm cannon is the designation for domestically produced \
variants of the Soviet 152mm towed field gun M1954 (M-47). The Reduced Variable charge is \
of bundle-and-loose-grain construction, with 0.25kg of 12/1 for the central bundle, and \
3.465 kg of loose 4/1 grains in charge bags. This case represents firing the reduced variable \
charge at the lower charge setting, wtih 2.05 kg of loose 4/1 left in. Nominal velocity \
is 380 m/s. Nominal pressure is >=900 kgf/cm^2 from copper crusher gauge.\n\
For this entry, the same charge properties as the preceeding entry has been used, with \
the exception of a reduced charge mass. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.876 * dm2,
    shot_mass=43.56,
    charge_mass=2.3,
    chamber_volume=17.27 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=55.77 * dm,
    charge=m_47_two.charge,
)

if __name__ == "__main__":
    from ballistics.state import StateList

    print(StateList.tabulate(m_47_full.to_travel()))
    print(StateList.tabulate(m_47_one.to_travel()))

    print(StateList.tabulate(m_47_two.to_travel()))

    print(StateList.tabulate(m_47_three.to_travel()))
