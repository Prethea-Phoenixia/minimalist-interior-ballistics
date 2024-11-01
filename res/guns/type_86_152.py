from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import (L, dm, dm2, dm3_kg, format_compo_string, kg_dm3, kgf_dm2,
                  kgfdm_kg)
from prop_9_7 import nine_seven, sb

df = Propellant(
    name="单芳-1",
    description="Values for this propellant is provisional.\n《火炮内弹道计算手册》(1987)",
    density=1.6 * kg_dm3,
    covolume=1.0 * dm3_kg,
    pressure_exponent=0.8,
    force=950000 * kgfdm_kg,
    adiabatic_index=1.2,
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
velocity is 955m/s. Pressure values have been converted from copper crusher gauge, as 310,000 \
kgf/dm^2.\n\
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
    pressure_target=PressureTarget(3282e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)

type_86_152_one = Gun(
    name="Type 1983/86 152mm Cannon (WB028 HE-Frag, Charge No.1)",
    description="Officially known as the Type 1986 152mm Cannon, earlier models were exported \
under the designation of Type 1983. The gun is provided with both a Full Variable and a Reduced \
Variable charge. This case represents firing with the Full Variable charge, in the reduced charge \
configuration. Nominal velocity is 890m/s. \n\
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
Variable charge. This case represents firing with the lowest configuration from the Reduced Variable \
charge. Nominal velocity is 540m/s. Pressure values have been converted from copper crusher \
gauge, as 96,000 kgf/dm^2.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=6.2,
    chamber_volume=30.57 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    propellant=sb,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(1054e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)


type_86_152_three = Gun(
    name="Type 1983/86 152mm Cannon (WB028 HE-Frag, Charge No.3)",
    description="Officially known as the Type 1986 152mm Cannon, earlier models were exported \
under the designation of Type 1983. The gun is provided with both a Full Variable and a Reduced \
Variable charge. This case represents firing with the medium configuration from the \
Reduced Variable charge. Nominal velocity is 660m/s.\n\
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

    print(StateList.tabulate(type_86_152_full.to_travel(n_intg=10)))
    print(StateList.tabulate(type_86_152_one.to_travel(n_intg=10)))
    print(StateList.tabulate(type_86_152_two.to_travel(n_intg=10)))
    print(StateList.tabulate(type_86_152_three.to_travel(n_intg=10)))
    print(StateList.tabulate(type_86_152_four.to_travel(n_intg=10)))
