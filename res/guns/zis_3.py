from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_9_7 import nine_seven, sb_9_7

zis_3_he_frag = KnownGunProblem(
    name="Type 1954 76mm Cannon (ZiS-3) (WB022P HE-Frag)",
    description="Type 1954 76mm Cannon is the domestic designation for the Soviet 76.2mm \
divisional gun M1942 (ZiS-3, GRAU index 52-P-354U). Nomianl velocity is 680-700 m/s developed at \
1.08 kg of charge. Nominal pressure is 2380 kgf/cm^2 from copper crusher gauge, converts \
to 2617 kgf/cm^2 actual. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.469 * dm2,
    shot_mass=6.2,
    charge_mass=1.08,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=26.87 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2617e2 * kgf_dm2),
)

zis_3_apcr = Gun(
    name="Type 1954 76mm Cannon (ZiS-3) (BR-350SP APBC)",
    description="Type 1954 76mm Cannon is the domestic designation for the Soviet 76.2mm \
divisional gun M1942 (ZiS-3, GRAU index 52-P-354U). Nomianl velocity is 655 m/s developed at \
1.08 kg of charge. Nominal pressure is 2400 kgf/cm^2 from copper crusher gauge. \n\
The charge design of the WB022P has been used. \
The equivalent Soviet shell is inferred from projectile mass.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.469 * dm2,
    shot_mass=6.5,
    charge_mass=1.08,
    chamber_volume=1.484 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=26.87 * dm,
    charge=zis_3_he_frag.charge,
)
if __name__ == "__main__":
    from ballistics.state import StateList

    print(StateList.tabulate(zis_3_he_frag.to_travel()))
    print(StateList.tabulate(zis_3_apcr.to_travel()))
