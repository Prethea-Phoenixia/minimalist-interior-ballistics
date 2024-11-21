from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_9_7 import nine_seven, sb_9_7
from prop_sf3 import sf3, sixteen_one

gun_intro = "The 152x346mm family of separately loaded, case charge munitions are issued to \
the Type 1966 152mm gun-howitzers, domestically produced variants of the Soviet 152mm gun-howitzer \
M1955 (D-20). The HE-Frag projectile is issued with either a full variable charge, or a reduced \
variable charge. \
The full variable charge loads 双芳-3 16/1 tubular grains, as well as minor amounts of 8/1 Rosin-\
Potassium grains as blast suppressant. The reduced variable charge loads 9/7 7 perforated grains \
as loose charge, with a central 4/1 tubular grain bundle. The full variable charge provides 2 \
zones, with 5 more from the reduced variable charge. \
"

gun_outro = "For simplicity, bundled charge has been treated as the equivalent mass in loose \
grains, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


full = KnownGunProblem(
    name="WB007P HE-Frag (Full Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the full variable charge as issued. Nominal velocity is 655 m/s. \
Nominal pressure is <=2350 kgf/cm^2 in copper crusher gauge. Computational values of 2581 and 2580 \
are attested in the source. For this example the final one has been adopted.",
            gun_outro,
        ]
    ),
    family="152x346mm",
    cross_section=1.875 * dm2,
    shot_mass=43.56,
    charge_mass=8.185,
    chamber_volume=12.505 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.9 * dm,
    propellant=sf3,
    form_function=sixteen_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2580e2 * kgf_dm2),
)

one = Gun(
    name="WB007P HE-Frag (No.1 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the full variable charge in No.1 charge configuration. \
Nominal velocity is 606 m/s. \
Nominal pressure is >=900 kgf/cm^2 in copper crusher gauge. Charge characteristics \
of the full charge has been adopted with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="152x346mm",
    cross_section=1.875 * dm2,
    shot_mass=43.56,
    charge_mass=7.295,
    chamber_volume=12.505 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.9 * dm,
    charge=full.charge,
)

two = KnownGunProblem(
    name="WB007P HE-Frag (No.2 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the reduced variable charge as issued. Nominal velocity of \
511 m/s.",
            gun_outro,
        ]
    ),
    family="152x346mm",
    cross_section=1.875 * dm2,
    shot_mass=43.56,
    charge_mass=4.14,
    chamber_volume=12.505 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.9 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2000e2 * kgf_dm2),
)


three = Gun(
    name="WB007P HE-Frag (No.3 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the reduced variable charge in zone 3 configuration. \
Nominal velocity of 427 m/s. Charge characteristics of No.2 charge has been \
adopted with a reduction in charge mass.",
            gun_outro,
        ]
    ),
    family="152x346mm",
    cross_section=1.875 * dm2,
    shot_mass=43.56,
    charge_mass=3.01,
    chamber_volume=12.505 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.9 * dm,
    charge=two.charge,
)

four = Gun(
    name="WB007P HE-Frag (No.4 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the reduced variable charge in zone 4 configuration. \
Nominal velocity of 380 m/s. Charge characteristics of No.2 charge has been \
adopted with a reduction in charge mass.",
            gun_outro,
        ]
    ),
    family="152x346mm",
    cross_section=1.875 * dm2,
    shot_mass=43.56,
    charge_mass=2.445,
    chamber_volume=12.505 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.9 * dm,
    charge=two.charge,
)


five = Gun(
    name="WB007P HE-Frag (No.5 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the reduced variable charge in zone 5 configuration. \
Charge characteristics of No.2 charge has been \
adopted with a reduction in charge mass.",
            gun_outro,
        ]
    ),
    family="152x346mm",
    cross_section=1.875 * dm2,
    shot_mass=43.56,
    charge_mass=1.88,
    chamber_volume=12.505 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.9 * dm,
    charge=two.charge,
)


six = Gun(
    name="WB007P HE-Frag (No.6 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the reduced variable charge in zone 6 configuration. \
Nominal velocity of 282 m/s. Charge characteristics of No.2 charge has been \
adopted with a reduction in charge mass.",
            gun_outro,
        ]
    ),
    family="152x346mm",
    cross_section=1.875 * dm2,
    shot_mass=43.56,
    charge_mass=1.315,
    chamber_volume=12.505 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.9 * dm,
    charge=two.charge,
)


all_guns = [full, one, two, three, four, five, six]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
