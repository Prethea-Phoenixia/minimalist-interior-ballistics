from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_11_7 import eleven_seven, sb_11_7

gun_intro = "The 57x347mm family of fixed charge ammunitions are issued to the Type 1959 57mm anti \
air gun, developed from the Soviet anti aircraft gun (AZP) S-60. \
The AP(T) and Frag(T) (timed fuze) projectiles shares the same propelling charge, which loads \
1.19 kg of 11/7 seven-perforated loose grains. "

gun_outro = "\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"

land = KnownGunProblem(
    name="WB011PG AP(T), WB107PG Frag(T)",
    description="\n".join(
        [
            gun_intro,
            "\
Nominal velocity is 1000 m/s. Nominal pressure is <=3100 kgf/cm^2 from copper crusher gauge. \
Example adopts pressure of 3203 kgf/cm^2 with an adopted charge mass of 1.07kg.",
            gun_outro,
        ]
    ),
    family="57x347mm",
    cross_section=0.27 * dm2,
    shot_mass=2.8,
    charge_mass=1.07,
    chamber_volume=1.51 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=36.24 * dm,
    propellant=sb_11_7,
    form_function=eleven_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(3203e2 * kgf_dm2),
)


all_guns = [land]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
