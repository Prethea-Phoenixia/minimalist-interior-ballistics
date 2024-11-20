from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, dm3_kg, kg_dm3, kgf_dm2, kgfdm_kg
from prop_9_7 import nine_seven, sb_9_7

df1 = Propellant(
    name="单芳-1",
    description="Values for this propellant is provisional.\n《火炮内弹道计算手册》(1987)",
    density=1.6 * kg_dm3,
    covolume=1.0 * dm3_kg,
    force=95e4 * kgfdm_kg,
    adiabatic_index=1.24,
)
twentytwo_seven = FormFunction.multi_perf(
    arch_width=mean((2.1, 2.4)),
    perforation_diameter=mean((0.95, 1.2)),
    height=mean((26, 30)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)

gun_intro = "The 152mm family of separately loaded, case charge munitions are issued to \
the Type 1986 152mm cannon, earlier models of which were exported under the designation of \
Type 1983. The gun is provided with both a full variable and a reduced variable charge. \
Note that thermalchemical properties of the 单芳-1 propellant are notional."

gun_outro = "For simplicity, bundled charge has been treated as the equivalent mass in loose \
grains, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"

type_86_152_full = KnownGunProblem(
    name="WB028 HE-Frag (Full Charge)",
    description="\n".join(
        [
            gun_intro,
            "This case represents firing with the full variable charge as issued. Nominal \
velocity is 955m/s. Nominal pressure is 3100 kgf/cm^2 from copper crusher gauge. Computational \
values of 3282 kgf/cm^2 is adopted.",
            gun_outro,
        ]
    ),
    family="152mm Type 86",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=21.09,
    chamber_volume=30.57 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    propellant=df1,
    form_function=twentytwo_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(3282e2 * kgf_dm2),
)

type_86_152_one = Gun(
    name="WB028 HE-Frag (Charge No.1)",
    description="\n".join(
        [
            gun_intro,
            "This case represents firing with the full variable charge, with charge bag taken \
out. Nominal velocity is 890m/s. This entry adopts the same properties of charge from the full \
charge entry, with a reduced charge mass.",
            gun_outro,
        ]
    ),
    family="152mm Type 86",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=18.8,
    chamber_volume=30.57 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    charge=type_86_152_full.charge,
)

type_86_152_two = KnownGunProblem(
    name="WB028 HE-Frag (Charge No.2)",
    description="\n".join(
        [
            gun_intro,
            "This case represents firing the reduced variable charge as issued. Nominal \
velocity is 780 m/s. Computational pressure of 2500 kgf/cm^2 has been adopted.",
            gun_outro,
        ]
    ),
    family="152mm Type 86",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=12,
    chamber_volume=30.57 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2500e2 * kgf_dm2),
)

type_86_152_three = Gun(
    name="WB028 HE-Frag (Charge No.3)",
    description="\n".join(
        [
            gun_intro,
            "This case represents firing the reduced variable charge as issued. Nominal \
velocity is 660 m/s. Charge characteristics of the No.2 charge has been adopted with a \
reduction in charge mass.",
            gun_outro,
        ]
    ),
    family="152mm Type 86",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=9.10,
    chamber_volume=30.57 * L,
    loss_fraction=0.05,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    charge=type_86_152_two.charge,
)


type_86_152_four = Gun(
    name="WB028 HE-Frag (Charge No.4)",
    description="\n".join(
        [
            gun_intro,
            "This case represents firing the reduced variable charge as issued. Nominal \
velocity is 540 m/s. Nominal pressure of >=960 kgf/cm^2 from copper crusher gauge is attested. \
Charge characteristics of the No.2 charge has been adopted with a reduction in charge mass.",
            gun_outro,
        ]
    ),
    family="152mm Type 86",
    cross_section=1.9045 * dm2,
    shot_mass=48,
    charge_mass=6.2,
    chamber_volume=30.57 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=70.91 * dm,
    charge=type_86_152_two.charge,
)


all_guns = [type_86_152_full, type_86_152_one, type_86_152_two, type_86_152_three, type_86_152_four]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
