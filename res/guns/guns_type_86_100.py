from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, dm3_kg, kg_dm3, kgf_dm2, kgfdm_kg

gdldjy = Propellant(
    name="高氮量单基药（可燃药筒）",
    description="《火炮内弹道计算手册》(1987)",
    density=1.6 * kg_dm3,
    covolume=0.95 * dm3_kg,
    pressure_exponent=0.84,
    force=1007000 * kgfdm_kg,
    adiabatic_index=1.2,
)
fourteen_nineteen = FormFunction.multi_perf(
    arch_width=1.48,
    perforation_diameter=0.46,
    height=10.74,
    shape=MultiPerfShape.NINETEEN_PERF_ROSETTE,
)


type_86_100_w_apfsds = KnownGunProblem(
    name="Type 1986 100mm High Pressure Smooth Bore Anti Tank Gun (Tungsten APFSDS)",
    description="Type 86 100 mm high pressure smooth bore anti tank gun is a further \
development of the domestic Type 73 100mm smoothbore anti tank gun, which was in turn \
a conversion of the Soviet BS-3 100mm field gun (and unrelated to the Soviet T-12 gun \
2A19). The 0.9kg combustible cartridge loads 5.79 kg of highly nitrated single based \
propellant. Nominal velocity is 1610 m/s - 1640 m/s. Nominal pressure is 4800 \
kgf/cm^2 from copper crusher gauge, converts to 4643 kgf/cm^2 actual. \n\
As the reference quoted was compiled using preliminary specification before type \
certification (in 1986), and as error has been identified in the source, more \
weight should be give to the commonly quoted, post type certification value of \
1610 m/s, reflected by this entry. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)",
    cross_section=0.7854 * dm2,
    shot_mass=5.3,
    charge_mass=6.69,
    chamber_volume=8.8 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.89 * dm,
    propellant=gdldjy,
    form_function=fourteen_nineteen,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(4643e2 * kgf_dm2),
)


all_guns = [type_86_100_w_apfsds]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
