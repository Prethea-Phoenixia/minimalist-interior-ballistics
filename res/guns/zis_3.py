from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_9_7 import nine_seven, sb_9_7

ref = "Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"

zis_3_he_frag = KnownGunProblem(
    name="Type 1954 76mm Cannon (ZiS-3) (WB022P HE-Frag)",
    description="Type 1954 76mm Cannon is the domestic designation for the Soviet 76.2mm \
divisional gun M1942 (ZiS-3, GRAU index 52-P-354U). Nomianl velocity is 680 m/s developed at \
1.08 kg of charge. Nominal pressure is 2380 kgf/cm^2 from copper crusher gauge. The adopted \
computational mean pressure level is 2620 kgf/cm^2. \n\
A slightly reduced charge to 0.98kg has been adopted to improve conformity with tabulated \
performance levels.\n"
    + ref,
    cross_section=0.469 * dm2,
    shot_mass=6.2,
    charge_mass=0.98,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=26.87 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2620e2 * kgf_dm2),
)

zis_3_apbc = Gun(
    name="Type 1954 76mm Cannon (ZiS-3) (BR-350SP APBC)",
    description="Type 1954 76mm Cannon is the domestic designation for the Soviet 76.2mm \
divisional gun M1942 (ZiS-3, GRAU index 52-P-354U). Nomianl velocity is 655 m/s developed at \
1.08 kg of charge. Nominal pressure is 2400 kgf/cm^2 from copper crusher gauge. \n\
The charge characteristics of the WB022P has been used, with a slightly reduced charge to \
0.94kg has been adopted. The equivalent Soviet shell is inferred from projectile mass.\n"
    + ref,
    cross_section=0.469 * dm2,
    shot_mass=6.5,
    charge_mass=0.94,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=26.87 * dm,
    charge=zis_3_he_frag.charge,
)

all_guns = [zis_3_apbc, zis_3_he_frag]
if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(StateList.tabulate(gun.to_travel()))
