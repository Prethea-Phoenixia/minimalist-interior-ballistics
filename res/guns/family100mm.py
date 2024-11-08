from statistics import mean

from ballistics.form_function import FormFunction
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_sf3 import sf3

gun_intro = "The 100mm family consists of fixed charge munitions issued \
to the Type 1959 100mm tank gun (domestically produced variant of the Soviet tank gun D-10T), \
and the Type 1959 100mm anti air gun (domestically produced variant of the Soviet anti air gun \
KS-19M2), and the Soviet field gun M1944 (BS-3) (domestically known as the Type 1944 cannon, \
domestically produced variant known as Type 1959). Cartridges were produced both in steel, copper, \
as well as with semi-combustible casings for tank guns.\n\
The APBC, HE-Frag, and the Airburst-Fragmentation projectiles shares the same propelling charge. \
The HE-Frag shell can also be issued with a reduced charge. The HEAT-FS projectile employs an \
alternative charge."

gun_outro = "For simplicity, bundled charge has been treated as the equivalent mass in loose \
rains, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"

eighteen_one = FormFunction.single_perf(arch_width=mean((1.67, 1.77)), height=260)
he_frag = KnownGunProblem(
    name="100mm High Explosive Fragmentation WB004P",
    description="\n".join(
        [
            gun_intro,
            "This example illustrate the WB004P HE-Frag shell fired with the full charge, \
which loads 5.5 or 5.66 kg of 18/1-26 long tubular grains, for copper and steel cartridges, \
respectively. The nominal velocity is 900 m/s, at a nomianl chamber pressure of 3000 kgf/cm^2 \
as measured from copper crusher gauges. Actual pressure used for computation has been variously \
reported as 3141 and 3300 kgf/cm^2. A value of 3220 kgf/cm^2 for a 5.5 kg charge has been adopted \
for this example.",
            gun_outro,
        ]
    ),
    cross_section=0.818 * dm2,
    shot_mass=15.6,
    charge_mass=5.5,
    chamber_volume=7.9 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.38 * dm,
    propellant=sf3,
    form_function=eighteen_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(3220e2 * kgf_dm2),
)


apbc = Gun(
    name="100mm Armor Piercing Ballistic Capped WB116P",
    description="\n".join(
        [
            gun_intro,
            "This example illustrate the WB116P armor piercing ballistic capped \
projectile with the full charge, \
which loads 5.5 or 5.66 kg of 18/1-26 long tubular grains, for copper and steel cartridges, \
respectively. Nominal velocity is given as 902.5m/s, or less commonly 887 m/s. Nominal \
pressure value is 3000 kgf/cm^2, from copper crusher gauge.\n\
The charge mass and characteristics of the WB004P full charge case has been used. Increase in \
velocity despite increased projectile weight is explained by longer obturated travel in bore, \
due to the more rearward positioning of the driving band.",
            gun_outro,
        ]
    ),
    cross_section=0.818 * dm2,
    shot_mass=15.88,
    charge_mass=5.5,
    chamber_volume=7.9 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=48.95 * dm,
    charge=he_frag.charge,
)
all_guns = [
    he_frag,
    apbc,
]


if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
