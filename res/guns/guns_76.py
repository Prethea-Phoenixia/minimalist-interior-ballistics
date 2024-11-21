from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_9_7 import nine_seven, sb_9_7

gun_intro = "The 76.2x385mm family of fixed charge ammunition is issued to the Soviet 76.2mm \
divisional gun M1942 (ZiS-3, GRAU index 52-P-354U), domestically produced as Type 1954 \
76mm cannon. The same ballistics applies to the D-56T rifled gun, mounted on the PT-76. \
Charge loads 9/7 7-perforated loose grains, to various mass depending on the particular \
projectile. \
"

gun_outro = "\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


of350 = KnownGunProblem(
    name="WB022P HE-Frag",
    description="\n".join(
        [
            gun_intro,
            "\
Nomianl velocity is 680 m/s developed at 1.07 or 1.08 kg of charge. Nominal pressure is \
2380 kgf/cm^2 from copper crusher gauge. Computational levels of 2500, 2617 and 2620 \
kgf/cm^2 has been tabulated. Match of tabulated performance established by reducing \
charge mass.",
            gun_outro,
        ]
    ),
    family="76.2x385mm",
    cross_section=0.469 * dm2,
    shot_mass=6.21,
    charge_mass=0.977,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=26.87 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2617e2 * kgf_dm2),
)

br350 = Gun(
    name="BR-350B APBC-HE",
    description="\n".join(
        [
            gun_intro,
            "\
Nomianl velocity is 655 m/s developed with 1.07 or 1.08 kg of charge. \
Nominal pressure is 2400 kgf/cm^2 from copper crusher gauge. \
Match of tabulated performance established by reducing charge mass.",
            gun_outro,
        ]
    ),
    family="76.2x385mm",
    cross_section=0.469 * dm2,
    shot_mass=6.5,
    charge_mass=0.945,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=26.87 * dm,
    charge=of350.charge,
)


br354p = Gun(
    name="BR-354P APCR",
    description="\n".join(
        [
            gun_intro,
            "Nominal velocity of 950 m/s. \
Match of tabulated performance established by reducing charge mass.",
            gun_outro,
        ]
    ),
    family="76.2x385mm",
    cross_section=0.469 * dm2,
    shot_mass=3.02,
    charge_mass=1.229,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=26.87 * dm,
    charge=of350.charge,
)

br354n = Gun(
    name="BR-354N APCR",
    description="\n".join(
        [
            gun_intro,
            "Nominal velocity of 950 m/s. \
Match of tabulated performance established by reducing charge mass.",
            gun_outro,
        ]
    ),
    family="76.2x385mm",
    cross_section=0.469 * dm2,
    shot_mass=3.3,
    charge_mass=1.25,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=26.87 * dm,
    charge=of350.charge,
)

bk354 = Gun(
    name="BK-354(M) HEAT-FS",
    description="\n".join(
        [
            gun_intro,
            "Nominal velocity of 550 m/s. \
Match of tabulated performance established by reducing charge mass.",
            gun_outro,
        ]
    ),
    family="76.2x385mm",
    cross_section=0.469 * dm2,
    shot_mass=7.027,
    charge_mass=0.756,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=26.87 * dm,
    charge=of350.charge,
)

all_guns = [of350, br350, br354p, br354n, bk354]
if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
