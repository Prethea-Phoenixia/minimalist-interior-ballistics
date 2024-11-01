from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import (L, dm, dm2, dm3_kg, format_compo_string, kg_dm3, kgf_dm2,
                  kgfdm_kg)

sb = Propellant(
    name="Single Base",
    description="2796 K, Nitrated to 204-207.5 mL/g\n\
《火炸药手册 (增订本）第二分册》(1981), 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
    density=1.6 * kg_dm3,
    force=1011300 * kgfdm_kg,
    pressure_exponent=0.84,
    covolume=0.95576 * dm3_kg,
    adiabatic_index=1.2391,
)

fourteen_seven = FormFunction.multi_perf(
    arch_width=mean((1.20, 1.55)),
    perforation_diameter=mean((0.7, 0.8)),
    height=mean((16, 18)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)

zis_2_he_frag = KnownGunProblem(
    name="Type 1955 57mm Cannon (ZiS-2) (WB009 HE-Frag)",
    description="Type 1955 57mm Cannon is the domestic designation for the Soviet 57mm \
anti-tank gun M1943 (ZiS-2, GRAU index 52-P-271). Nominal velcoity at 700 m/s. Pressure \
values have been converted from copper crusher gauge, at 180,000 kgf/dm^2.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.2663 * dm2,
    shot_mass=3.75,
    charge_mass=0.98,
    chamber_volume=1.875 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=35.66 * dm,
    propellant=sb,
    form_function=fourteen_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(
        2004e2 * kgf_dm2,
        target=PressureTarget.AVERAGE,
    ),
)


def copper_correction(projectile_mass: float, charge_mass: float):
    phi = 1.05 + charge_mass / projectile_mass / 3
    return 1.12 * phi / (1.02 * (1 + 0.4649 * charge_mass / projectile_mass))


zis_2_apcbc = KnownGunProblem(
    name="Type 1955 57mm Cannon (ZiS-2) (BR-271M APCBC-T)",
    description="Type 1955 57mm Cannon is the domestic designation for the Soviet 57mm \
anti-tank gun M1943 (ZiS-2, GRAU index 52-P-271). Nominal velocity of 1040 m/s. Pressure \
values are converted from copper crusher gauge, nominally 310,000 kgf/dm^2.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.2663 * dm2,
    shot_mass=2.8,
    charge_mass=1.47,
    chamber_volume=1.875 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=35.66 * dm,
    propellant=sb,
    form_function=fourteen_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(
        3100e2 * kgf_dm2 * copper_correction(projectile_mass=2.8, charge_mass=1.47),
        target=PressureTarget.AVERAGE,
    ),
)

sb = Propellant(
    name="Single Base",
    description="2822 K, Nitrated to 204-207.5 mL/g\n\
《火炸药手册 (增订本）第二分册》(1981), 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
    density=1.6 * kg_dm3,
    force=1015100 * kgfdm_kg,
    pressure_exponent=0.84,
    covolume=0.95074 * dm3_kg,
    adiabatic_index=1.2381,
)

twelve_seven = FormFunction.multi_perf(
    arch_width=mean((1.10, 1.30)),
    perforation_diameter=mean((0.50, 0.70)),
    height=mean((13.5, 15.6)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)

zis_2_apcr = KnownGunProblem(
    name="Type 1955 57mm Cannon (ZiS-2) (BR-271P APCR)",
    description="Type 1955 57mm Cannon is the domestic designation for the Soviet 57mm \
anti-tank gun M1943 (ZiS-2, GRAU index 52-P-271). Nominal velocity of 1250 m/s. Pressure \
values are converted from copper crusher gauge, nominally 310,000 kgf/dm^2.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.2663 * dm2,
    shot_mass=1.79,
    charge_mass=1.6,
    chamber_volume=1.875 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=35.66 * dm,
    propellant=sb,
    form_function=twelve_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(
        3100e2 * kgf_dm2 * copper_correction(projectile_mass=1.79, charge_mass=1.6),
        target=PressureTarget.AVERAGE,
    ),
)


if __name__ == "__main__":
    from ballistics.state import StateList

    print(StateList.tabulate(zis_2_he_frag.to_travel(n_intg=10)))

    print(StateList.tabulate(zis_2_apcbc.to_travel(n_intg=10)))
    print(StateList.tabulate(zis_2_apcr.to_travel(n_intg=10)))
