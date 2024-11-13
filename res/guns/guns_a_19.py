from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_yf3 import seventeen_one, yf3

gun_intro = "\
The 122mm family of separately loaded, cased charge munitions are issued to the Soviet 122mm corps \
gun M1931/1937 (A-19), domestically designated the Type 1931/1937, as well as tank guns based on \
the ballistics of the A-19, including the A-19S, the D-25T and the D-25S guns.\n\
The APHE, APHEBC and HE-Frag projectiles, all of equal weight, shares the same four stage variable \
charge, which loads 17/1 bundled tubular grains of 乙芳-3 propellant. The charge consists of a base \
charge of 4.35 kg, a central bundle on top of 1.077 kg, and two equal-weight bundles surrounding \
the central bundle, of 0.71kg each."

gun_outro = "\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


full = KnownGunProblem(
    name="122mm WB013P HE-Frag (Full)",
    description="\n".join(
        [
            gun_intro,
            "\
Fired as issued, 800 m/s of nominal velocity is developed at 2750 kgf/cm^2 of average pressure, \
measured from copper crusher gauge. Computational values of 2897 or 3000 kgf/cm^2 are known. \
The former value is adopted for this example, which yields accurate result, with no entry worse \
than 5 m/s off nominal.\n\
This entry is also representative of the APHE and APHEBC projectiles since these shares the same \
interior ballistics.",
            gun_outro,
        ]
    ),
    cross_section=1.188 * dm2,
    shot_mass=25,
    charge_mass=6.824,
    chamber_volume=9.898 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.55 * dm,
    propellant=yf3,
    form_function=seventeen_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(2897e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)

no_1 = Gun(
    name="122mm WB013P HE-Frag (No.1 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
Extracting one equal-weight bundle forms the No.1 charge. Nominal velocity is 742 m/s. The charge \
characteristics of the full charge has been used with a reduction in charge mass to yield this \
entry.",
            gun_outro,
        ]
    ),
    cross_section=1.188 * dm2,
    shot_mass=25,
    charge_mass=6.124,
    chamber_volume=9.898 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.55 * dm,
    charge=full.charge,
)

no_2 = Gun(
    name="122mm WB013P HE-Frag (No.2 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
Extracting both equal-weight bundles forms the No.2 charge. Nominal velocity is 680 m/s. The \
charge characteristics of the full charge has been used with a reduction in charge mass to yield \
this entry.",
            gun_outro,
        ]
    ),
    cross_section=1.188 * dm2,
    shot_mass=25,
    charge_mass=5.424,
    chamber_volume=9.898 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.55 * dm,
    charge=full.charge,
)

no_3 = Gun(
    name="122mm WB013P HE-Frag (No.3 Charge)",
    description="\n".join(
        [
            gun_intro,
            "\
Extracting both equal-weight bundles, as well as the central bundle forms the No.3 charge. \
Nominal velocity is 570 m/s. The charge \
characteristics of the full charge has been used with a reduction in charge mass to yield this \
entry.",
            gun_outro,
        ]
    ),
    cross_section=1.188 * dm2,
    shot_mass=25,
    charge_mass=4.350,
    chamber_volume=9.898 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.55 * dm,
    charge=full.charge,
)

all_guns = [full, no_1, no_2, no_3]
if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
