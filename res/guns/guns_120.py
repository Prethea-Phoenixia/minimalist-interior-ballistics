from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_9_7 import nine_seven, sb_9_7
from prop_13_7 import sb_13_7, thirteen_seven
from prop_15_7 import fifteen_seven, sb_15_7

gun_intro = "The 120x790mm smoothbore family consists of fixed charge munitions issued \
to the 120mm smoothbore gun, provisionally fitted to the WZ-122 project. \
Charges are specific to each projectile type.\
"

gun_outro = "For simplicity, bundled charge has been treated as the equivalent mass in loose \
grains, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


he_frag = KnownGunProblem(
    name="WB032P HE-Frag-FS",
    description="\n".join(
        [
            gun_intro,
            "\
The WB129P HE-Frag-FS projectiles are fired with a fixed charge, with 6.4 kg of propellant. \
1 kg of 18/1-33 single perforated tubular grain is bundled in the center. \
15/7 seven perforated loose grains makes up the rest. \
The nominal pressure developed is <=2400 kgf/cm^2. The computational value of 2607 kgf/cm^2. \
has been adopted per source. Nominal velocity of 940 m/s is developed.",
            gun_outro,
        ]
    ),
    family="120x790mm",
    cross_section=1.131 * dm2,
    shot_mass=16.5,
    charge_mass=6.4,
    chamber_volume=10.15 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=51.11 * dm,
    propellant=sb_15_7,
    form_function=fifteen_seven,
).get_gun_developing_pressure(pressure_target=PressureTarget.average_pressure(2607e2 * kgf_dm2))


heat = KnownGunProblem(
    name="WB129P HEAT-FS",
    description="\n".join(
        [
            gun_intro,
            "\
The WB129P HEAT-FS projectiles are fired with a fixed charge, with 6.431 kg of propellant. \
1 kg of 18/1-33 single perforated tubular grain is bundled in the center. \
13/7 7 perforated loose grains makes up the rest. \
The nominal pressure developed is <=2500 kgf/cm^2. The computational value of 2716 kgf/cm^2. \
has been adopted per source. Nominal velocity of 1000 m/s is developed.",
            gun_outro,
        ]
    ),
    family="120x790mm",
    cross_section=1.131 * dm2,
    shot_mass=15,
    charge_mass=6.431,
    chamber_volume=10.15 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=51.11 * dm,
    propellant=sb_13_7,
    form_function=thirteen_seven,
).get_gun_developing_pressure(pressure_target=PressureTarget.average_pressure(2716e2 * kgf_dm2))


apfsds = KnownGunProblem(
    name="APFSDS for Type 71",
    description="\n".join(
        [
            gun_intro,
            "\
The APFSDS projectiles are fired with a fixed charge, with 8.4 kg of propellant. \
1 kg of 18/1-33 single perforated tubular grain is bundled in the center. \
9/7 7 perforated loose grains makes up the rest. \
The nominal pressure developed is <=3280 kgf/cm^2. The computational value of 3280 kgf/cm^2. \
has been adopted per source. Nominal velocity of >=1580 m/s is developed.",
            gun_outro,
        ]
    ),
    family="120x790mm",
    cross_section=1.131 * dm2,
    shot_mass=6,
    charge_mass=8.4,
    chamber_volume=11.78 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=50 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(pressure_target=PressureTarget.average_pressure(3280e2 * kgf_dm2))


all_guns = [heat, he_frag, apfsds]
if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
