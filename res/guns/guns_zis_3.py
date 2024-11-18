from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_9_7 import nine_seven, sb_9_7

ref = "Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"

gun_intro = "The 76.2x385mm fixed ammunition family is issued to the Soviet 76.2mm \
divisional gun M1942 (ZiS-3, GRAU index 52-P-354U), domestically produced as Type 1954 \
76mm cannon. The same ballistics applies to the D-56T rifled gun, mounted on the PT-76. \
The HE-Frag and APBC projectiles share a charge of 9/7 7-perforated loose grains. \
"

gun_outro = "\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"

zis_3_he_frag = KnownGunProblem(
    name="WB022P HE-Frag",
    description="\n".join(
        [
            gun_intro,
            "\
Nomianl velocity is 680 m/s developed at 1.07 or 1.08 kg of charge. Nominal pressure is \
2380 kgf/cm^2 from copper crusher gauge. Computational levels of 2500, 2617 and 2620 \
kgf/cm^2 has been tabulated. The middle value with a charge mass of 1.01 kg has been adopted.",
            gun_outro,
        ]
    ),
    family="76.2x385mm",
    cross_section=0.469 * dm2,
    shot_mass=6.2,
    charge_mass=1.01,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=500e2 * kgf_dm2,
    travel=26.87 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2617e2 * kgf_dm2),
)

zis_3_apbc = Gun(
    name="BR-350B APBC",
    description="\n".join(
        [
            gun_intro,
            "\
Nomianl velocity is 655 m/s developed with 1.07 or 1.08 kg of charge. \
Nominal pressure is 2400 kgf/cm^2 from copper crusher gauge.\n\
The charge characteristics of the WB022P has been used, with a slight reduction in \
charge mass to 0.97kg to represent the deeper seated projectile.",
            gun_outro,
        ]
    ),
    family="76.2x385mm",
    cross_section=0.469 * dm2,
    shot_mass=6.5,
    charge_mass=0.97,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=500e2 * kgf_dm2,
    travel=26.87 * dm,
    charge=zis_3_he_frag.charge,
)

all_guns = [zis_3_apbc, zis_3_he_frag]
if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
