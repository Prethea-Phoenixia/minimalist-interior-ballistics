from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_9_7 import nine_seven, sb_9_7
from prop_13_7 import sb_13_7, thirteen_seven
from prop_sf3 import eighteen_one, sf3

gun_intro = "The 100mm (rifled) family consists of fixed charge munitions issued \
to the Type 1959 100mm tank gun (domestically produced variant of the Soviet tank gun D-10T), \
and the Type 1959 100mm anti air gun (domestically produced variant of the Soviet anti air gun \
KS-19M2), and the Type 1959 100mm field gun (domestically produced variants of the Soviet field \
gun M1944 (BS-3)). Cartridges were produced with metallic casings, in steel and copper, as well \
with semi-combustible casings for tank guns.\n\
The APBC, HE-Frag, and the Airburst-Fragmentation projectiles shares the same propelling charge. \
The HE-Frag shell can also be issued with a reduced charge. The HEAT-FS projectile employs an \
alternative charge."

gun_outro = "For simplicity, bundled charge has been treated as the equivalent mass in loose \
grains, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


he_frag = KnownGunProblem(
    name="WB004P HE-Frag, WB016P, WB435P AB-Frag",
    description="\n".join(
        [
            gun_intro,
            "This example illustrate the WB004P HE-Frag shell, WB016P and WB435P proximity fuzed \
airburst-fragmentation round fired with the full charge, which loads 5.5 or 5.66 kg of 18/1-26 \
long tubular grains, for copper and steel cartridges, respectively. The nominal velocity is 900 \
- 902.5 m/s , at a nomianl chamber pressure of 3000 kgf/cm^2 \
as measured from copper crusher gauges. Actual pressure used for computation has been variously \
reported as 3141 and 3300 kgf/cm^2. A value of 3206 kgf/cm^2 for a 5.5 kg charge has been adopted \
for this example.",
            gun_outro,
        ]
    ),
    family="100x695mm",
    cross_section=0.818 * dm2,
    shot_mass=15.6,
    charge_mass=5.5,
    chamber_volume=7.985 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.43 * dm,
    propellant=sf3,
    form_function=eighteen_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(3206e2 * kgf_dm2),
)


he_frag_reduced = KnownGunProblem(
    name="WB004P HE-Frag (Reduced Charge)",
    description="\n".join(
        [
            gun_intro,
            "This example illustrate the WB004P HE-Frag shell fired with the reduced charge, \
which loads 12/1 tubular grains in a central bundle, with loose 9/7 grains bringing the total \
charge mass to 2.39 kg. Nominal velocity is 600 m/s. Nominal pressure is <= 2000 kgf/cm^2. A \
computational value of 1300 kgf/cm^2 has been adopted.",
            gun_outro,
        ]
    ),
    family="100x695mm",
    cross_section=0.818 * dm2,
    shot_mass=15.6,
    charge_mass=2.39,
    chamber_volume=7.985 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.43 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(1300e2 * kgf_dm2),
)

apbc = Gun(
    name="WB116P APBC(T)",
    description="\n".join(
        [
            gun_intro,
            "This example illustrate the WB116P armor piercing ballistic capped tracer \
projectile with the full charge, which loads 5.5 or 5.66 kg of 18/1-26 long tubular \
grains, for copper and steel cartridges, respectively. Nominal velocity is given as 902.5m/s, \
or less commonly 887 m/s. Nominal pressure value is 3000 kgf/cm^2, from copper crusher gauge.\n\
The charge mass and characteristics of the WB004P full charge case has been used. Increase in \
velocity despite increased projectile weight is explained by longer obturated travel in bore, \
due to the more rearward positioning of the driving band.",
            gun_outro,
        ]
    ),
    family="100x695mm",
    cross_section=0.818 * dm2,
    shot_mass=15.88,
    charge_mass=5.5,
    chamber_volume=7.983 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=49 * dm,
    charge=he_frag.charge,
)


heat = KnownGunProblem(
    name="WB122P Universal HEAT-FS ",
    description="\n".join(
        [
            gun_intro,
            "\
The WB122P round is universal in the sense that it can be fired from the rifled 100 mm\
family, including the Type 1959 100mm tank gun, anti-air gun, and towed field gun, \
as well as the smoothbore 100mm family, \
including the Type 1969 smoothbore tank guns, Type 1971/1973 smoothbore anti tank guns, \
and Type 1986 high pressure smoothbore anti tank guns. When fired from rifled guns, \
combustion gas partially blow past the projectile through the lands of the rifling. \
This is not well modelled, and consequently the calculated performance is only applicable \
to smoothbore barrels.\n\
This example illustrate the WB122P universal fin stabilized high explosive anti tank round \
fired from the rifled bore of this family, with its specific charge, which consists of \
0.14 kg of 10/1 Rosin-Potassium tubular grains as flash suppressant, and 0.82 kg of 18/1 of \
tubular grains bundled together in the center, with 3.84 kg of 13/7 loose grains making up the \
rest. Nominal velocity is given as 1000 m/s when fired from rifled guns, although value as low \
as 955 m/s has been seen in domestic sources. Fired from smoothbore guns, velocity as high as \
1070 m/s has been quoted. Nominal pressure value is 2530 kgf/cm^2, from copper crusher gauge. \
The adopted computational value is 2930 kgf/cm^2.",
            gun_outro,
        ]
    ),
    family="100x695mm",
    cross_section=0.818 * dm2,
    shot_mass=10.05,
    charge_mass=4.8,
    chamber_volume=7.83 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.94 * dm,
    propellant=sb_13_7,
    form_function=thirteen_seven,
).get_gun_developing_pressure(pressure_target=PressureTarget.average_pressure(2930e2 * kgf_dm2))

all_guns = [heat, apbc, he_frag, he_frag_reduced]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
