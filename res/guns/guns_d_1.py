from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_12_7 import sb_12_7_low, twelve_seven

gun_intro = "The 152x305mm family of separately loaded, case charge munitions are issued to \
the Type 1956 152mm howitzer, domestically produced variants of the Soviet 152mm howitzer \
M1943 (D-1). The HE-Frag projectile is issued with a full variable charge. The full variable \
charge contains four equi-weight top charge bags of 12/7 7 perforated \
grains, each weigh 0.53kg, and four equai-weight bottom charge bags of 12/7 7 perforated grains, \
each weigh 0.215kg. A bundle of 0.64kg of 4/1 tubular propellant is set in the center. \
"

gun_outro = "For simplicity, bundled charge has been treated as the equivalent mass in loose \
grains, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


def charge_mass(top: int, bottom: int):
    return 0.53 * top + 0.215 * bottom + 0.64


full = KnownGunProblem(
    name="WB006P HE-Frag (Full Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the charge as issued. Nominal velocity is 508 m/s. \
Nominal pressure is 2250 kgf/cm^2 in copper crusher gauge. Computational values of 2550 and 2553 \
are attested in the source. For this example the final one has been adopted.",
            gun_outro,
        ]
    ),
    family="152x305mm",
    cross_section=1.852 * dm2,
    shot_mass=40,
    charge_mass=charge_mass(top=4, bottom=4),
    chamber_volume=5.707 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=32.2 * dm,
    propellant=sb_12_7_low,
    form_function=twelve_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2553e2 * kgf_dm2),
)


one = Gun(
    name="WB006P HE-Frag (No.1 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the charge with one top charge bag removed. \
Nominal veloicty is 456 m/s. \
Charge characteristics of the full charge has been adopted, with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="152x305mm",
    cross_section=1.852 * dm2,
    shot_mass=40,
    charge_mass=charge_mass(top=3, bottom=4),
    chamber_volume=5.707 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=32.2 * dm,
    charge=full.charge,
)

two = Gun(
    name="WB006P HE-Frag (No.2 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the charge with two top charge bag removed. \
Nominal veloicty is 403 m/s. \
Charge characteristics of the full charge has been adopted, with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="152x305mm",
    cross_section=1.852 * dm2,
    shot_mass=40,
    charge_mass=charge_mass(top=2, bottom=4),
    chamber_volume=5.707 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=32.2 * dm,
    charge=full.charge,
)

three = Gun(
    name="WB006P HE-Frag (No.3 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the charge with three top charge bag removed. \
Nominal veloicty is 351 m/s. \
Charge characteristics of the full charge has been adopted, with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="152x305mm",
    cross_section=1.852 * dm2,
    shot_mass=40,
    charge_mass=charge_mass(top=1, bottom=4),
    chamber_volume=5.707 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=32.2 * dm,
    charge=full.charge,
)

four = Gun(
    name="WB006P HE-Frag (No.4 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the charge with all top charge bag removed. \
Nominal veloicty is 300 m/s. \
Charge characteristics of the full charge has been adopted, with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="152x305mm",
    cross_section=1.852 * dm2,
    shot_mass=40,
    charge_mass=charge_mass(top=0, bottom=4),
    chamber_volume=5.707 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=32.2 * dm,
    charge=full.charge,
)


five = Gun(
    name="WB006P HE-Frag (No.5 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the charge with all top and one bottom charge bags removed. \
Nominal veloicty is 279 m/s. \
Charge characteristics of the full charge has been adopted, with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="152x305mm",
    cross_section=1.852 * dm2,
    shot_mass=40,
    charge_mass=charge_mass(top=0, bottom=3),
    chamber_volume=5.707 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=32.2 * dm,
    charge=full.charge,
)


six = Gun(
    name="WB006P HE-Frag (No.6 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the charge with all top and two bottom charge bags removed. \
Nominal veloicty is 258 m/s. \
Charge characteristics of the full charge has been adopted, with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="152x305mm",
    cross_section=1.852 * dm2,
    shot_mass=40,
    charge_mass=charge_mass(top=0, bottom=2),
    chamber_volume=5.707 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=32.2 * dm,
    charge=full.charge,
)


seven = Gun(
    name="WB006P HE-Frag (No.7 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the charge with all top and three bottom charge bags removed. \
Nominal veloicty is 236 m/s. \
Charge characteristics of the full charge has been adopted, with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="152x305mm",
    cross_section=1.852 * dm2,
    shot_mass=40,
    charge_mass=charge_mass(top=0, bottom=1),
    chamber_volume=5.707 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=32.2 * dm,
    charge=full.charge,
)


eight = Gun(
    name="WB006P HE-Frag (No.8 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the charge with all top and bottom charge bags removed. \
Nominal veloicty is 213 m/s. \
Charge characteristics of the full charge has been adopted, with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="152x305mm",
    cross_section=1.852 * dm2,
    shot_mass=40,
    charge_mass=charge_mass(top=0, bottom=0),
    chamber_volume=5.707 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=32.2 * dm,
    charge=full.charge,
)


all_guns = [full, one, two, three, four, five, six, seven, eight]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
