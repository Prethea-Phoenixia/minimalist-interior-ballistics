from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_13_7 import sb_13_7, thirteen_seven
from prop_sf2 import nineteen_one, sf2

gun_intro = "\
The 122mm family of separately loaded, cased charge munitions are issued to Type 60 122mm gun, \
domestic produced variant of the Soviet 122mm field gun D-74. \
The HE-Frag, Smoke, Illumination, and Incendiary projectiles are issued with a full charge, \
and a reduced variable charge. The full charge loads 9.8 kg of 双芳-2 19/1 tubular grains, \
while the reduced variable charge loads up to 5.83 kg of 13/7 loose grains, in various \
charge bags. 0.7 kg of 12/1 Rosin-Potassium tubular charge is bundled in the center. \
This provides 1 velocity zone for the full charge, and 3 velocity zones for the reduced \
variable charge. \
The APBC(T) projectile is issued with a dedicated charge for firing."


gun_outro = "\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


full = KnownGunProblem(
    name="WB010P HE-Frag (Full Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This illustrates the WB010P HE-Frag projectile, fired with the full charge as issued, \
885 m/s of nominal velocity is developed at 3150 kgf/cm^2 of average pressure, \
measured from copper crusher gauge. Computational values of 3280 or 3700 kgf/cm^2 are known. \
A value of 3460 kgf/cm^2 has been adopted. \
",
            gun_outro,
        ]
    ),
    family="122x760mm",
    cross_section=1.212 * dm2,
    shot_mass=27.3,
    charge_mass=9.8,
    chamber_volume=14.03 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=49.101 * dm,
    propellant=sf2,
    form_function=nineteen_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(3460e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)


one = KnownGunProblem(
    name="WB010P HE-Frag (No.1 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This illustrates the WB010P HE-Frag projectile, fired with the reduced variable charge as issued, \
770 m/s of nominal velocity is developed at 3150 kgf/cm^2 of average pressure, \
measured from copper crusher gauge. Computational values of 2900 kgf/cm^2 has been adopted. This \
results in match of better than 2 m/s for all reduced charge zones. \
",
            gun_outro,
        ]
    ),
    family="122x760mm",
    cross_section=1.212 * dm2,
    shot_mass=27.3,
    charge_mass=6.53,
    chamber_volume=14.03 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=49.101 * dm,
    propellant=sb_13_7,
    form_function=thirteen_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(2900e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)

two = Gun(
    name="WB010P HE-Frag (No.2 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This illustrates the WB010P HE-Frag projectile, fired with the reduced variable charge, with \
one charge bag taken out. \
660 m/s of nominal velocity is developed. Charge characteristics of the No.1 Charge has been \
adopted, with a reduction in charge mass.\
",
            gun_outro,
        ]
    ),
    family="122x760mm",
    cross_section=1.212 * dm2,
    shot_mass=27.3,
    charge_mass=5.14,
    chamber_volume=14.03 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=49.101 * dm,
    charge=one.charge,
)

three = Gun(
    name="WB010P HE-Frag (No.3 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This illustrates the WB010P HE-Frag projectile, fired with the reduced variable charge, with \
two charge bag taken out. \
550 m/s of nominal velocity is developed. Charge characteristics of the No.1 Charge has been \
adopted, with a reduction in charge mass.\
",
            gun_outro,
        ]
    ),
    family="122x760mm",
    cross_section=1.212 * dm2,
    shot_mass=27.3,
    charge_mass=3.75,
    chamber_volume=14.03 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=49.101 * dm,
    charge=one.charge,
)

all_guns = [full, one, two, three]
if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
