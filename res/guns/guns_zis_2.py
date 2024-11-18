from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_12_7 import sb_12_7, twelve_seven
from prop_14_7 import fourteen_seven, sb_14_7

ref = "Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


def copper_correction(projectile_mass: float, charge_mass: float):
    phi = 1.05 + charge_mass / projectile_mass / 3
    return 1.12 * phi / (1.02 * (1 + 0.4649 * charge_mass / projectile_mass))


# print(1800 * copper_correction(projectile_mass=3.75, charge_mass=0.98))

zis_2_he_frag = KnownGunProblem(
    name="WB009P HE-Frag",
    description="Type 1955 57mm Cannon is the domestic designation for the Soviet 57mm \
anti-tank gun M1943 (ZiS-2, GRAU index 52-P-271). Nominal velocity at 700/706 m/s. Nominal \
pressure is 1700/1800 kgf/cm^2 from copper crusher gauge.\n\
The different tabulated values for muzzle velocity realtes to the difference in construction \
of the driving band (s) -- single driving band projectiles develops 1700 kgf/cm^2 of pressure, \
and achieves a velocity of 700 m/s, while double driving band projectiles develops 1800 \
kgf/cm^2 of pressure. A computational value of 2000 kgf/cm^2 has been adopted.\n\
"
    # A major reduction in charge mass, from the nominal value of 0.98 kg, to 0.75kg, is required \
    # to match the tabulated performance. The significance of this is currently not well understood.\n"
    + ref,
    family="57×480mm",
    cross_section=0.2663 * dm2,
    shot_mass=3.75,
    charge_mass=(w := 0.98),
    chamber_volume=1.875 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=35.66 * dm,
    propellant=sb_14_7,
    form_function=fourteen_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2000e2 * kgf_dm2 * copper_correction(3.75, w))
)

# print(3100 * copper_correction(projectile_mass=2.8, charge_mass=1.47))

zis_2_apcbc = KnownGunProblem(
    name="BR-271M APBC-T",
    description="Type 1955 57mm Cannon is the domestic designation for the Soviet 57mm \
anti-tank gun M1943 (ZiS-2, GRAU index 52-P-271). Nominal velocity of 1040 m/s. Nominal \
pressure of 3100 kgf/cm^2 in copper crusher gauge.\n\
The reference listed does not direclty refer to the shell type under consideration, the \
equivalent Soviet projectile is inferred from the weight used in calculation.\n\
A major reduction in charge mass, from the nominal value of 1.47 kg, to 1.3 kg, is required \
to match the tabulated performance. The significance of this is currently not well understood. \n"
    + ref,
    family="57×480mm",
    cross_section=0.2663 * dm2,
    shot_mass=2.8,
    charge_mass=(w := 1.3),
    chamber_volume=1.875 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=35.66 * dm,
    propellant=sb_14_7,
    form_function=fourteen_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(3100e2 * kgf_dm2 * copper_correction(2.8, w)),
)


# print(3100 * copper_correction(projectile_mass=1.79, charge_mass=1.6))
zis_2_apcr = KnownGunProblem(
    name="BR-271P APCR",
    description="Type 1955 57mm Cannon is the domestic designation for the Soviet 57mm \
anti-tank gun M1943 (ZiS-2, GRAU index 52-P-271). Nominal velocity of >1250 m/s. Nominal pressure \
at 3100 kgf/cm^2 in copper crusher gauge.\n\
The reference listed does not direclty refer to the shell type under consideration, the \
equivalent Soviet projectile is inferred from the weight used in calculation.\n\
A major reduction in charge mass, from the nominal value of 1.6 kg, to 1.28 kg, is required \
to match the tabulated performance. The significance of this is currently not well understood.\n"
    + ref,
    family="57×480mm",
    cross_section=0.2663 * dm2,
    shot_mass=1.79,
    charge_mass=(w := 1.28),
    chamber_volume=1.875 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=35.66 * dm,
    propellant=sb_12_7,
    form_function=twelve_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(3100e2 * kgf_dm2 * copper_correction(1.79, w))
)


# all_guns = [zis_2_apcr, zis_2_apcbc, zis_2_he_frag]
# too many issues.
if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
