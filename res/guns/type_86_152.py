from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, dm3_kg, kg_dm3, kgf_dm2, kgfdm_kg
from prop_9_7 import nine_seven, sb_9_7

df = Propellant(
    name="单芳-1",
    description="Values for this propellant is provisional.\n《火炮内弹道计算手册》(1987)",
    density=1.6 * kg_dm3,
    covolume=1.0 * dm3_kg,
    pressure_exponent=0.82,
    force=930000 * kgfdm_kg,
    adiabatic_index=1.24,
)
twentytwo_seven = FormFunction.multi_perf(
    arch_width=mean((2.1, 2.4)),
    perforation_diameter=mean((0.95, 1.2)),
    height=mean((26, 30)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)


type_86_152_full = KnownGunProblem(
    name="Type 1983/86 152mm Cannon (WB028 HE-Frag, Full Charge)",
    description="Officially known as the Type 1986 152mm Cannon, earlier models were exported \
under the designation of Type 1983. The gun is provided with both a Full Variable and a Reduced \
Variable charge. This case represents firing with the Full Variable charge as issued. Nominal \
velocity is 955m/s. Nominal pressure is 3100 kgf/cm^2 from copper crusher gauge, converts to \
3282 kgf/cm^2 actual.\n\
Since the 单芳-1 is completley undocumented, the thermalchemical properties of the charge is \
manipulated until a reasonable match for the two Full Variable charge zones are found. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=21.09,
    chamber_volume=30.57 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    propellant=df,
    form_function=twentytwo_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(3282e2 * kgf_dm2),
)

type_86_152_one = Gun(
    name="Type 1983/86 152mm Cannon (WB028 HE-Frag, Charge No.1)",
    description="Officially known as the Type 1986 152mm Cannon, earlier models were exported \
under the designation of Type 1983. The gun is provided with both a Full Variable and a Reduced \
Variable charge. This case represents firing with the Full Variable charge, in the reduced charge \
configuration. Nominal velocity is 890m/s. \n\
This entry adopts the same properties of charge from the preceeding entry, with a reduced \
charge mass. Due to the circumstance documented above, no further adjustment is made for better \
conformity.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=18.8,
    chamber_volume=30.57 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    charge=type_86_152_full.charge,
)


type_86_152_four = KnownGunProblem(
    name="Type 1983/86 152mm Cannon (WB028 HE-Frag, Charge No.4)",
    description="Officially known as the Type 1986 152mm Cannon, earlier models were exported \
under the designation of Type 1983. The gun is provided with both a Full Variable and a Reduced \
Variable charge. This case represents firing with the lowest configuration from the Reduced \
Variable charge. Nominal velocity is 540m/s. Nominal pressure is >=960 kgf/cm^2 from copper \
crusher, converts to 1054 kgf/cm^2 actual.\n\
Given the Type 83/86 design is sparsely documented, although the results does not exactly \
duplicated tabulated values, the match is considered reasonable enough such that no further \
adjustments are made to improve conformity. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=6.2,
    chamber_volume=30.57 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(900e2 * kgf_dm2),
)


type_86_152_three = Gun(
    name="Type 1983/86 152mm Cannon (WB028 HE-Frag, Charge No.3)",
    description="Officially known as the Type 1986 152mm Cannon, earlier models were exported \
under the designation of Type 1983. The gun is provided with both a Full Variable and a Reduced \
Variable charge. This case represents firing with the medium configuration from the \
Reduced Variable charge. Nominal velocity is 660m/s.\n\
The charge characteristics of the No.4 charge zone has been used, with an increase in charge \
mass. \
Given the Type 83/86 design is sparsely documented, although the results does not exactly \
duplicated tabulated values, the match is considered reasonable enough such that no further \
adjustments are made to improve conformity. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=9.10,
    chamber_volume=30.57 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    charge=type_86_152_four.charge,
)

type_86_152_two = Gun(
    name="Type 1983/86 152mm Cannon (WB028 HE-Frag, Charge No.2)",
    description="Officially known as the Type 1986 152mm Cannon, earlier models were exported \
under the designation of Type 1983. The gun is provided with both a Full Variable and a Reduced \
Variable charge. This case rrepresents firing the Reduced Variable charge as issued. \
Nominal velocity is 780m/s.\n\
The charge characteristics of the No.4 charge zone has been used, with an increase in charge \
mass. \
Given the Type 83/86 design is sparsely documented, although the results does not exactly \
duplicated tabulated values, the match is considered reasonable enough such that no further \
adjustments are made to improve conformity. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=12,
    chamber_volume=30.57 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    charge=type_86_152_four.charge,
)

if __name__ == "__main__":
    from ballistics.state import StateList

    print(type_86_152_full.name)
    print(StateList.tabulate(type_86_152_full.to_travel(n_intg=10)))
    print(type_86_152_one.name)
    print(StateList.tabulate(type_86_152_one.to_travel(n_intg=10)))
    print(type_86_152_two.name)
    print(StateList.tabulate(type_86_152_two.to_travel(n_intg=10)))
    print(type_86_152_three.name)
    print(StateList.tabulate(type_86_152_three.to_travel(n_intg=10)))
    print(type_86_152_four.name)
    print(StateList.tabulate(type_86_152_four.to_travel(n_intg=10)))
