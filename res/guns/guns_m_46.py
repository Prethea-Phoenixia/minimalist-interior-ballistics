from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_9_7 import nine_seven, sb_9_7
from prop_sf3 import sf3, twentythree_one

gun_intro = "The 130mm family of separately loaded, case charge munitions are issued to \
the Type 1959 130mm cannon, domestically produced variants of the Soviet 130mm towed field gun \
M1954 (M-46, GRAU Index 52-P-482). The HE-Frag projectile is issued with either a full variable \
or a reduced variable charge. The APHE projectile is fired with the full charge as issued. \n\
The full variable charge is supplied with various charge bags of 双芳-3 23/1 tubular grains, \
totaling 12.9kg. This provides two velocity zones. \
The reduced variable charge is supplied with a 0.7 kg bundle of 7/1 propellant, \
and multiple bags of 9/7 loose grains totaling 5.82 kg. This provides three further velocity \
zones.\
"

gun_outro = "For simplicity, bundled charge has been treated as the equivalent mass in loose \
grains, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


full = KnownGunProblem(
    name="130mm WB005P HE-Frag (Full Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents when firing the charge as issued. Nominal velocity is 930m/s. \
Nominal pressure is 3150 kgf/cm^2 in copper crusher gauge. Computational values of 3370 \
and 3465 kgf/cm^2 are attested in the source.",
            gun_outro,
        ]
    ),
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=12.9,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=59.52 * dm,
    propellant=sf3,
    form_function=twentythree_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(3370e2 * kgf_dm2),
)

one = Gun(
    name="130mm WB005P HE-Frag (No.1 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the full variable charge with a supplementary charge bag of 1.9kg \
taken out. Nominal velocity is 810m/s. This entry adopts the same properties of charge from the \
full charge entry, with a reduction in charge mass. ",
            gun_outro,
        ]
    ),
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=11,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=59.52 * dm,
    charge=full.charge,
)


two = KnownGunProblem(
    name="130mm WB005P HE-Frag (No.2 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the reduced variable charge as issued. \
Nominal velocity is 705m/s. Nominal pressure is <=2700 kgf/cm^2 in copper crusher gauge. \
A computational value of 2365 kgf/cm^2 is adopted.",
            gun_outro,
        ]
    ),
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=6.520,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=59.52 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(value=2365e2 * kgf_dm2)
)

three = Gun(
    name="130mm WB005P HE-Frag (No.3 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing with one balanced increments removed, Nominal velocity is \
620 m/s. Characteristics of charge from the No.2 entry has been used with a reduction \
in charge mass.",
            gun_outro,
        ]
    ),
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=5.220,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=59.52 * dm,
    charge=two.charge,
)


four = Gun(
    name="130mm WB005P HE-Frag (No.4 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
This case represents firing the reduced variable charge with two balanced increments removed. \
Nominal velocity is 525m/s. Nominal pressure is >=1100 kgf/cm^2 in copper crusher gauge. \
This entry adopts the same properties of charge from the No.2 charge entry, with a reduction \
in charge mass.",
            gun_outro,
        ]
    ),
    cross_section=1.394 * dm2,
    shot_mass=33.4,
    charge_mass=3.920,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=59.52 * dm,
    charge=two.charge,
)

all_guns = [full, one, two, three, four]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
