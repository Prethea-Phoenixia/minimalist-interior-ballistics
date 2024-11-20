from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_9_7 import nine_seven, sb_9_7_low

gun_intro = "The 122x285mm family of separately loaded, case charge munitions are issued to \
the Type 1954 122mm howitzer, domestically produced variants of the Soviet 122mm howitzer \
M1938 (M-30, GRAU Index 52-G-463). The HE-Frag projectile is issued with a full variable \
charge. The full variable charge contains four equi-weight top charge bags of 9/7 7 perforated \
grains, each weigh 0.325kg, and four equai-weight bottom charge bags of 9/7 7 perforated grains, \
each weigh 0.115kg. A bundle of 0.34kg of 4/1 tubular propellant is set in the center. \
"

gun_outro = "For simplicity, bundled charge has been treated as the equivalent mass in loose \
grains, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


def charge_mass(top: int, bottom: int):
    return 0.325 * top + 0.115 * bottom + 0.34


full = KnownGunProblem(
    name="WB012P HE-Frag (Full Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents when firing the charge as issued. Nominal velocity is 515 m/s. \
Nominal pressure is 2350 kgf/cm^2 in copper crusher gauge. Computational values of 2470, 2580 \
and 2665 kgf/cm^2 are attested in the source. For this example the final one has \
been adopted.",
            gun_outro,
        ]
    ),
    family="122x285mm",
    cross_section=1.196 * dm2,
    shot_mass=21.76,
    charge_mass=charge_mass(top=4, bottom=4),
    chamber_volume=3.77 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=23.84 * dm,
    propellant=sb_9_7_low,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2665e2 * kgf_dm2),
)


one = Gun(
    name="WB012P HE-Frag (No.1)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents when firing with one top charge bag removed. \
Nominal velocity is 458 m/s. Charge characteristics of the full charge has been adopted, \
with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="122x285mm",
    cross_section=1.196 * dm2,
    shot_mass=21.76,
    charge_mass=charge_mass(top=3, bottom=4),
    chamber_volume=3.77 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=23.84 * dm,
    charge=full.charge,
)

two = Gun(
    name="WB012P HE-Frag (No.2)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents when firing with two top bag removed. \
Nominal velocity is 402 m/s. Charge characteristics of the full charge has been adopted, \
with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="122x285mm",
    cross_section=1.196 * dm2,
    shot_mass=21.76,
    charge_mass=charge_mass(top=2, bottom=4),
    chamber_volume=3.77 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=23.84 * dm,
    charge=full.charge,
)

three = Gun(
    name="WB012P HE-Frag (No.3)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents when firing with three top bag removed. \
Nominal velocity is 346 m/s. Charge characteristics of the full charge has been adopted, \
with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="122x285mm",
    cross_section=1.196 * dm2,
    shot_mass=21.76,
    charge_mass=charge_mass(top=1, bottom=4),
    chamber_volume=3.77 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=23.84 * dm,
    charge=full.charge,
)


four = Gun(
    name="WB012P HE-Frag (No.4)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents when firing with all top charge bags removed. \
Nominal velocity is 290 m/s. Charge characteristics of the full charge has been adopted, \
with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="122x285mm",
    cross_section=1.196 * dm2,
    shot_mass=21.76,
    charge_mass=charge_mass(top=0, bottom=4),
    chamber_volume=3.77 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=23.84 * dm,
    charge=full.charge,
)

five = Gun(
    name="WB012P HE-Frag (No.5)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents when firing with all top charge bags, and one bottom charge bag \
removed. Nominal velocity is 269 m/s. Charge characteristics of the full charge has been adopted, \
with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="122x285mm",
    cross_section=1.196 * dm2,
    shot_mass=21.76,
    charge_mass=charge_mass(top=0, bottom=3),
    chamber_volume=3.77 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=23.84 * dm,
    charge=full.charge,
)

six = Gun(
    name="WB012P HE-Frag (No.6)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents when firing with all top charge bags, and two bottom charge bag \
removed. Nominal velocity is 248 m/s. Charge characteristics of the full charge has been adopted, \
with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="122x285mm",
    cross_section=1.196 * dm2,
    shot_mass=21.76,
    charge_mass=charge_mass(top=0, bottom=2),
    chamber_volume=3.77 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=23.84 * dm,
    charge=full.charge,
)


seven = Gun(
    name="WB012P HE-Frag (No.7)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents when firing with all top charge bags, and three bottom charge bag \
removed. Nominal velocity is 227 m/s. Charge characteristics of the full charge has been adopted, \
with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="122x285mm",
    cross_section=1.196 * dm2,
    shot_mass=21.76,
    charge_mass=charge_mass(top=0, bottom=1),
    chamber_volume=3.77 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=23.84 * dm,
    charge=full.charge,
)


eight = Gun(
    name="WB012P HE-Frag (No.8)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents when firing with all top and bottom charge bags \
removed. Nominal velocity is 205 m/s. Charge characteristics of the full charge has been adopted, \
with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    family="122x285mm",
    cross_section=1.196 * dm2,
    shot_mass=21.76,
    charge_mass=charge_mass(top=0, bottom=0),
    chamber_volume=3.77 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=23.84 * dm,
    charge=full.charge,
)


all_guns = [full, one, two, three, four, five, six, seven, eight]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
