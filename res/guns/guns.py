from statistics import mean

from minimalist_interior_ballistics.charge import Charge, Propellant
from minimalist_interior_ballistics.form_function import FormFunction, MultiPerfShape
from minimalist_interior_ballistics.gun import Gun
from minimalist_interior_ballistics.problem import KnownGunProblem, PressureTarget

dm = 1e-1
dm2 = 1e-2
L = 1e-3
kg_dm3 = 1e3
dm3_kg = 1e-3
kgfdm_kg = 0.98
kgf_dm2 = 980
dm_s = 0.1
mm = 1e-3

NDT_3 = Propellant(
    name="НДТ-3",
    density=1.6 * kg_dm3,
    force=960e3,
    pressure_exponent=1,
    burn_rate_coefficient=5.61e-10,
    covolume=1.0e-3,
    adiabatic_index=1.2,
)


"""
used in: 
-----------------------
                BS-3
18/1    100     D-10 
                KS-19
-----------------------
19/1    152.4   M-47
-----------------------
23/1    130     M-46
-----------------------
"""


pyroxylin = Propellant(
    name="pyroxylin",
    density=1600,
    force=950e3,
    pressure_exponent=1,
    burn_rate_coefficient=5.2e-10,
    covolume=1.0e-3,
    adiabatic_index=1.2,
)

pyroxylin_perforated = Propellant(
    name="pyroxylin (perforated)",
    density=1600,
    force=950e3,
    pressure_exponent=0.83,
    burn_rate_coefficient=1.7e-8,
    covolume=1.0e-3,
    adiabatic_index=1.25,
)


four_one = FormFunction.single_perf(arch_width=0.4250 * mm, height=6.5 * mm)
eighteen_one = FormFunction.single_perf(arch_width=1.8 * mm, height=260 * mm)
nineteen_one = FormFunction.single_perf(arch_width=1.9 * mm, height=320 * mm)
twentythree_one = FormFunction.single_perf(arch_width=2.3 * mm, height=370 * mm)
twelve_one = FormFunction.single_perf(arch_width=1.2 * mm)

nine_seven = FormFunction.multi_perf(
    arch_width=1.025 * mm, perforation_diameter=0.5 * mm, height=12.05 * mm, shape=MultiPerfShape.SEVEN_PERF_CYLINDER
)
eleven_seven = FormFunction.multi_perf(
    arch_width=mean((1.00, 1.15)) * mm,
    perforation_diameter=mean((0.45, 0.65)) * mm,
    height=mean((11.5, 15.5)) * mm,
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)
twelve_seven = FormFunction.multi_perf(
    arch_width=mean((1.10, 1.30)) * mm,
    perforation_diameter=mean((0.50, 0.70)) * mm,
    height=mean((13.5, 15.6)) * mm,
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)
thirteen_seven = fourteen_seven = FormFunction.multi_perf(
    arch_width=mean((1.30, 1.40)) * mm,
    perforation_diameter=mean((0.5, 0.7)) * mm,
    height=mean((13.0, 15.0)) * mm,
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)
fourteen_seven = FormFunction.multi_perf(
    arch_width=mean((1.20, 1.55)) * mm,
    perforation_diameter=mean((0.7, 0.8)) * mm,
    height=mean((16.0, 18.0)) * mm,
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)


ZiS_2_UO_271U = Gun(
    name="УО-271У",
    description="57x480, 700,706m/s, nominal 0.94kg, 1800 kgf/dm^2",
    family="ЗиС-2",
    shot_mass=3.75,
    cross_section=0.2663 * dm2,
    charge=Charge.from_propellant(propellant=pyroxylin_perforated, form_function=twelve_seven),
    charge_mass=0.94,
    chamber_volume=1.875 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=35.66 * dm,
)


ZiS_2_UBR_271M = Gun(
    name="УБР-271М",
    description="57x480, 1040 m/s, nominal 1.5kg, 3100 kgf/dm^2",
    family="ЗиС-2",
    shot_mass=2.8,
    cross_section=0.2663 * dm2,
    charge=Charge.from_propellant(propellant=pyroxylin_perforated, form_function=twelve_seven),
    charge_mass=1.5,
    chamber_volume=1.875 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=35.66 * dm,
)


ZiS_2_UBR_271P = Gun(
    name="УБР-271П",
    description="57x480, >=1270m/s, nominal 1.6kg, 3100 kgf/dm^2",
    family="ЗиС-2",
    shot_mass=1.79,
    cross_section=0.2663 * dm2,
    charge=Charge.from_propellant(propellant=pyroxylin_perforated, form_function=twelve_seven),
    charge_mass=1.6,
    chamber_volume=1.875 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=35.66 * dm,
)


BS_3_full = Gun(
    name="УОФ-412",
    description="ОФ-412 w/ normal charge\nnominal: 5.5 kg of NDT-3 18/1, 900 m/s, <=3000 kgf/cm^2 pressure",
    family="БС-3",
    shot_mass=15.6,
    cross_section=0.818 * dm2,
    charge=Charge.from_propellant(
        propellant=NDT_3,
        form_function=eighteen_one,
    ),
    charge_mass=5.5,
    chamber_volume=7.9 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=47.38 * dm,
)


BS_3_reduced = Gun(
    name="УОФ-412У",
    description="ОФ-412 w/ reduced charge\nnominal: 2.4 kg of 9/7, 600 m/s, <=2000 kgf/cm^2 pressure",
    family="БС-3",
    shot_mass=15.6,
    cross_section=0.818 * dm2,
    charge=Charge.from_propellant(propellant=pyroxylin_perforated, form_function=nine_seven),
    charge_mass=2.4,
    chamber_volume=7.9 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=47.38 * dm,
)

BS_3_ap = Gun(
    name="УБР-412",
    description="БР-412 w/ normal charge\nnominal: 5.5 kg of NDT-3 18/1, 895 m/s, <=3000 kgf/cm^2 pressure",
    family="БС-3",
    shot_mass=15.88,
    cross_section=0.818 * dm2,
    charge=Charge.from_propellant(propellant=NDT_3, form_function=eighteen_one),
    charge_mass=5.5,
    chamber_volume=7.9 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=47.38 * dm,
)


M_47_full = Gun(
    name="53-УОФ-547",
    description="53-ОФ-547 w/ full variable charge\nnominal: 10.67 kg NDT-3 19/1-32, 770 m/s, <=2350 kgf/cm^2 average",
    family="M-47 52-П-547",
    shot_mass=43.56,
    cross_section=1.876 * dm2,
    charge=Charge.from_propellant(
        propellant=NDT_3,
        form_function=nineteen_one,
    ),
    charge_mass=10.67,
    chamber_volume=17.27 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=55.77 * dm,
)

M_47_first = Gun(
    name="53-УОФ-547 -1 Charge Bag",
    description="53-ОФ-547 w/ full variable charge\nnominal: 8.45 kg NDT-3 19/1-32, 635 m/s, <=1000 kgf/cm^2 average",
    family="M-47 52-П-547",
    shot_mass=43.56,
    cross_section=1.876 * dm2,
    charge=Charge.from_propellant(propellant=NDT_3, form_function=nineteen_one),
    charge_mass=8.45,
    chamber_volume=17.27 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=55.77 * dm,
)


M_47_second = Gun(
    name="53-УОФ-547У",
    description="53-ОФ-547 w/ reduced variable charge\nnominal: 3.465 kg 4/1 + 0.25 kg 12/1, 500 m/s, <=2350 kgf/cm^2 average",
    family="M-47 52-П-547",
    shot_mass=43.56,
    cross_section=1.876 * dm2,
    charges=[
        Charge.from_propellant(propellant=pyroxylin, form_function=four_one),
        Charge.from_propellant(propellant=pyroxylin, form_function=twelve_one),
    ],
    charge_masses=[3.465, 0.25],
    chamber_volume=17.27 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=55.77 * dm,
)


M_47_third = Gun(
    name="53-УОФ-547У",
    description="53-ОФ-547 w/ reduced variable charge\nnominal: 2.05 kg 4/1 + 0.25 kg 12/1, 380 m/s, <=900 kgf/cm^2 average",
    family="M-47 52-П-547",
    shot_mass=43.56,
    cross_section=1.876 * dm2,
    charges=[
        Charge.from_propellant(propellant=pyroxylin, form_function=four_one),
        Charge.from_propellant(propellant=pyroxylin, form_function=twelve_one),
    ],
    charge_masses=[2.05, 0.25],
    chamber_volume=17.27 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=55.77 * dm,
)


M_46_full = Gun(
    name="3ВОФ11",
    description="3ОФ3 w/ full variable charge\nnominal: 12.9 kg NDT-3 23/1, 930 m/s, <=3150 kgf/cm^2 average",
    family="M-46 52-П-482",
    shot_mass=33.4,
    cross_section=1.394 * dm2,
    charge=Charge.from_propellant(propellant=NDT_3, form_function=twentythree_one),
    charge_mass=12.9,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=59.52 * dm,
)

M_46_first = Gun(
    name="3ВОФ11 -1 Charge Bag",
    description="3ОФ3 w/ full variable charge\nnominal: 11.0 kg NDT-3 23/1, 810 m/s, <=3000 kgf/cm^2 average",
    family="M-46 52-П-482",
    shot_mass=33.4,
    cross_section=1.394 * dm2,
    charge=Charge.from_propellant(propellant=NDT_3, form_function=twentythree_one),
    charge_mass=11.0,
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=59.52 * dm,
)


M_46_second = Gun(
    name="3ВОФ12",
    description="3ОФ3 w/ reduced variable charge\nnominal: 5.8 kg 9/7 + 0.70 kg 12/1, 705 m/s, <=2700 kgf/cm^2 average",
    family="M-46 52-П-482",
    shot_mass=33.4,
    cross_section=1.394 * dm2,
    charges=[
        Charge.from_propellant(propellant=pyroxylin_perforated, form_function=nine_seven),
        Charge.from_propellant(propellant=pyroxylin, form_function=twelve_one),
    ],
    charge_masses=[5.8, 0.7],
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=59.52 * dm,
)

M_46_third = Gun(
    name="3ВОФ12 -1 Charge Bag",
    description="3ОФ3 w/ reduced variable charge\nnominal: 4.52 kg 9/7 + 0.70 kg 12/1, 620 m/s",
    family="M-46 52-П-482",
    shot_mass=33.4,
    cross_section=1.394 * dm2,
    charges=[
        Charge.from_propellant(propellant=pyroxylin_perforated, form_function=nine_seven),
        Charge.from_propellant(propellant=pyroxylin, form_function=twelve_one),
    ],
    charge_masses=[4.52, 0.7],
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=59.52 * dm,
)

M_46_fourth = Gun(
    name="3ВОФ12 -2 Charge Bags",
    description="3ОФ3 w/ reduced variable charge\nnominal: 3.22 kg 9/7 + 0.70 kg 12/1, 525 m/s, <=1100 kgf/cm^2 average",
    family="M-46 52-П-482",
    shot_mass=33.4,
    cross_section=1.394 * dm2,
    charges=[
        Charge.from_propellant(propellant=pyroxylin_perforated, form_function=nine_seven),
        Charge.from_propellant(propellant=pyroxylin, form_function=twelve_one),
    ],
    charge_masses=[3.22, 0.7],
    chamber_volume=18.58 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=59.52 * dm,
)


S_60 = Gun(
    name="УОР-,УБР-281(У)",
    description="57×348 мм, nominal: <1.19kg 11/7, 1000 m/s, 3100 kgf/dm^2",
    family="С-60",
    shot_mass=2.8,
    cross_section=0.2663 * dm2,
    charge=Charge.from_propellant(propellant=pyroxylin_perforated, form_function=eleven_seven),
    charge_mass=1.16,
    chamber_volume=1.51 * L,
    loss_fraction=0.03,
    start_pressure=30e6,
    travel=36.24 * dm,
)


all_guns = [
    ZiS_2_UO_271U,
    ZiS_2_UBR_271M,
    ZiS_2_UBR_271P,
    BS_3_full,
    BS_3_reduced,
    BS_3_ap,
    M_47_full,
    M_47_first,
    M_47_second,
    M_47_third,
    M_46_full,
    M_46_first,
    M_46_second,
    M_46_third,
    M_46_fourth,
    S_60,
]


if __name__ == "__main__":
    from minimalist_interior_ballistics.state import StateList

    family_dict = {}

    for gun in all_guns:
        if gun.family not in family_dict:
            family_dict[gun.family] = [gun]
        else:
            family_dict[gun.family].append(gun)

    for family, guns in family_dict.items():

        with open(f"texts/{family}.txt", mode="w+") as file:

            for gun in guns:
                # register guns by their family:
                file.write(f"{gun.name:-<100}\n\n")
                file.write(gun.description + "\n\n")
                file.write(StateList.tabulate(gun.to_travel(), tablefmt="grid") + "\n")
                file.write("\n\n")
