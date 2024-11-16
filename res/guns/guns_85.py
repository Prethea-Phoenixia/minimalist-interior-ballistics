from ballistics.gun import Gun, GunFamily
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_7_7 import sb_7_7, seven_seven
from prop_9_7 import nine_seven, sb_9_7
from prop_11_7 import eleven_seven, sb_11_7
from prop_14_7 import fourteen_seven, sb_14_7

gun_intro = "The 85mm family consists of fixed charge munitions issued \
to the Soviet tank gun ZiS-S-53 (domestically known as the 85mm tank gun), \
the Soviet 85mm divisional gun D-44 (including its domestically produced \
variant, Type 1956 85mm cannon), and with the Soviet 85mm air defense gun M1939 (52-K) \
(domestically known as the Type 1939 85mm anti-air gun).\n\
The AP, APBC, and APCR projectiles shares \
the same charge as the full charge for the HE-Frag shells. The HE-Frag shells are also \
issued with an reduced charge of similar construction. APCR shells are issued with an alternative \
charge. Finally, the HEAT-FS and HESH projectiles share a charge design, with the HESH projectile \
using a reduced charge."

gun_outro = "For simplicity, and in accordance with the treatment detailed in the sources, the \
bundled charge has been treated as the equivalent mass in loose grains, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"

full = KnownGunProblem(
    name="WB014P, WB024P HE-Frag (Full Charge)",
    description="\n".join(
        [
            gun_intro,
            "This example illustrates the normal HE-Frag shell WB014P, or the nodular cast iron \
shell WB024P, fired with the full charge, which loads a central bundle \
of 18/1-42, and loose grains of 14/7 brings the total mass of 2.48-2.63 kg. The nominal velocity \
is between 785 - 793 m/s, with a nominal pressure of 2550 kgf/cm^2 from copper crusher gauge. \
The adopted computational average pressure is 2850 kgf/cm^2. Matching to established performance \
by varying charge mass.",
            gun_outro,
        ]
    ),
    cross_section=0.582 * dm2,
    shot_mass=9.54,
    charge_mass=2.37,
    chamber_volume=3.94 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.92 * dm,
    propellant=sb_14_7,
    form_function=fourteen_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2850e2 * kgf_dm2),
)

reduced = KnownGunProblem(
    name="WB014P, WB024P HE-Frag (Reduced Charge)",
    description="\n".join(
        [
            gun_intro,
            "This example illustrates the normal HE-Frag shell WB014P, or the nodular cast iron \
shell WB024P, fired with the reduced charge, which loads a central bundle \
of 12/1, and loose grains of 7/7 brings the total mass of 1.50 kg. The nominal velocity \
is around 655 m/s, with a nominal pressure of 2350 kgf/cm^2 from copper crusher gauge. \
The adopted computational average pressure is 2650 kgf/cm^2. No adjustment is necessary.\
Matching to established performance by varying charge mass.",
            gun_outro,
        ]
    ),
    cross_section=0.582 * dm2,
    shot_mass=9.54,
    charge_mass=1.45,
    chamber_volume=3.94 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.92 * dm,
    propellant=sb_7_7,
    form_function=seven_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2650e2 * kgf_dm2),
)

ap = Gun(
    name="WB101P AP(T)",
    description="\n".join(
        [
            gun_intro,
            "This example illustrates WB101P armor piercing (tracer) projectile, fired with \
the full charge, which loads a central bundle of 18/1-42, and loose grains of 14/7 brings the \
total mass to 2.48-2.63 kg. The nominal velocity is 800 m/s, with a nominal pressure \
of 2550 kgf/cm^2 from copper crusher gauge. The adopted computational average pressure is \
2800 kgf/cm^2. Same charge characteristics used as the HE-Frag w/full charge. \
Matching to established performance by varying charge mass.",
            gun_outro,
        ]
    ),
    cross_section=0.582 * dm2,
    shot_mass=9.342,
    charge_mass=2.4,
    chamber_volume=3.985 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.46 * dm,
    charge=full.charge,
)

apbc = Gun(
    name="WB114P APBC(T) ",
    description="\n".join(
        [
            gun_intro,
            "This example illustrates WB114P armor piercing ballistic capped (tracer) \
projectile, fired with the full charge, which loads a central bundle of 18/1-42, and loose grains \
of 14/7 brings the total mass to 2.48-2.63 kg. The nominal velocity is 805 m/s, \
with a nominal pressure of 2550 kgf/cm^2 from copper crusher gauge. The adopted computational \
average pressure is 2800 kgf/cm^2. Same charge characteristics used as the HE-Frag w/full charge. \
Matching to established performance by varying charge mass.",
            gun_outro,
        ]
    ),
    cross_section=0.582 * dm2,
    shot_mass=9.2,
    charge_mass=2.41,
    chamber_volume=4 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.46 * dm,
    charge=full.charge,
)

apcr = KnownGunProblem(
    name="WB102P APCR(T)",
    description="\n".join(
        [
            gun_intro,
            "This example illustrates firing the WB102P armor piercing composite rigid (tracer) \
projectile with its specific charge, which loads a central bundle of 12/1-32, and loose grains of \
9/7 brings the total mass to 2.5-2.76 kg. The nominal velocity is 1050m/s, with a nominal \
pressure of 2550 kgf/cm^2 from copper crusher gauge. The adopted computational average pressure \
is 2800 kgf/cm^2. Matching to established performance by varying charge mass.",
            gun_outro,
        ]
    ),
    cross_section=0.582 * dm2,
    shot_mass=4.99,
    charge_mass=2.345,
    chamber_volume=4.12 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.49 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2800e2 * kgf_dm2),
)


heat = KnownGunProblem(
    name="WB109AP HEAT-FS",
    description="\n".join(
        [
            gun_intro,
            "This example illustrates the WB109AP fin stabilized high explosive anti tank \
projectile, fired with the full alternative charge, which loads loose grains of 11/7 up to 2.236 \
kg. The nominal velocity is 845 m/s, with a nominal \
pressure of 2350 kgf/cm^2 from copper crusher gauge. The adopted computational average pressure \
is 2643 kgf/cm^2. Matching to established performance by varying charge mass.",
            gun_outro,
        ]
    ),
    cross_section=0.582 * dm2,
    shot_mass=7,
    charge_mass=1.898,
    chamber_volume=3.628 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.82 * dm,
    propellant=sb_11_7,
    form_function=eleven_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2643e2 * kgf_dm2),
)

hesh = Gun(
    name="WB128P HESH ",
    description="\n".join(
        [
            gun_intro,
            "This example illustrates the WB128P high explosive squashed head \
projectile, fired with the reduced alternative charge, which loads loose grains of 11/7 up to 1.9 \
kg. The nominal velocity is 730 m/s, with a nominal pressure of 1685 kgf/cm^2 from copper crusher \
gauge. The adopted computational average pressure is 1900 kgf/cm^2. \
Matching to established performance by varying charge mass.",
            gun_outro,
        ]
    ),
    cross_section=0.582 * dm2,
    shot_mass=7,
    charge_mass=1.573,
    chamber_volume=4.02 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.07 * dm,
    charge=heat.charge,
)


all_guns = [apcr, heat, ap, apbc, full, reduced, hesh]
family = GunFamily(name="85x630mm Rifled")
for gun in all_guns:
    family.add_gun(gun)

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
