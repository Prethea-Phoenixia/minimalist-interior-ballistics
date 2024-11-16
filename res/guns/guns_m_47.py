from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_4_1 import four_one, sb_4_1
from prop_sf3 import nineteen_one, sf3

gun_intro = "The 152mm family of separately loaded, case charge munitions are issued to \
the Type 1959 152mm cannon, domestically produced variants of the Soviet 152mm towed field gun \
M1953 (M-47). The HE-Frag projectile is either issued with a full variable or a reduced \
variable charge. \n\
The Full Variable charge consists of several charge bags of 双芳-3 19/1 tubular grains weighing \
8.45kg, and supplementary charge bags of the same bringing the full charge to 10.67 kg. \
The Reduced Variable charge is of bundle-and-loose-grain construction, with 0.25kg of 12/1 for the \
central bundle, and 3.465 kg of loose 4/1 grains in charge bags. \
This provides two velocity zones for the full variable charge, and two additional zones for the \
reduced variable charge. \
An API projectile is also available, however the charge design for it is unknown at this time.\
"

gun_outro = "For simplicity, bundled charge has been treated as the equivalent mass in loose \
grains, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"

m_47_full = KnownGunProblem(
    name="WB008P HE-Frag (Full Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This example illustrates firing the WB008P HE-Frag projectile with the full variable charge \
as issued. \
Nominal velocity is 770 m/s. Nominal pressure is 2350 kgf/cm^2 from copper cursher gauge. \
The adopted computational values of 2570 or 2580 kgf/cm^2 have been attested to.",
            gun_outro,
        ]
    ),
    family="152x750mm",
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
    pressure_target=PressureTarget(2570e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)

m_47_one = Gun(
    name="WB008P HE-Frag (No.1 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This example illustrates firing the WB008P HE-Frag projectile with the full variable charge \
with the supplementary charge bag taken out. \
Nominal velocity is 635 m/s. Charge characteristics of the full charge has been adopted, \
with an reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="152x750mm",
    cross_section=1.876 * dm2,
    shot_mass=43.56,
    charge_mass=8.45,
    chamber_volume=17.27 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=55.77 * dm,
    charge=m_47_full.charge,
)


m_47_two = KnownGunProblem(
    name="WB008P HE-Frag (No.2 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This example illustrates firing the WB008P HE-Frag projectile with the reduced variable \
charge as issued. \
Nominal velocity is 500 m/s. Nominal pressure is <= 2350 kgf/cm^2 from copper crusher \
gauge. Adopted computational value is 1550 kgf/cm^2 ",
            gun_outro,
        ]
    ),
    family="152x750mm",
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
    name="WB008P HE-Frag (No.3 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This example illustrates firing the WB008P HE-Frag projectile with a charge bag removed from \
the reduced variable charge. \
Nominal velocity is 380 m/s. Nominal pressure is >=900 kgf/cm^2 from copper crusher \
gauge. Charge characteristics has been adopted from the No.2 charge entry, with an reduction in \
charge mass.",
            gun_outro,
        ]
    ),
    family="152x750mm",
    cross_section=1.876 * dm2,
    shot_mass=43.56,
    charge_mass=2.3,
    chamber_volume=17.27 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=55.77 * dm,
    charge=m_47_two.charge,
)

all_guns = [m_47_full, m_47_one, m_47_two, m_47_three]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
