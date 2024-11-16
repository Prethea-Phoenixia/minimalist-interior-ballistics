from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, dm3_kg, kg_dm3, kgf_dm2, kgfdm_kg
from prop_9_7 import nine_seven, sb_9_7
from prop_20_1 import sb_20_1, twenty_one

gdldjy = Propellant(
    name="高氮量单基药（含可燃药筒）",
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


gun_intro = "The 100 mm family of smoothbore munitions are issued to the Type 1969 tank gun and \
the Type 1971/1973 100mm smoothbore anti tank gun, both of which a conversion of the Soviet BS-3 \
100mm (rifled) field gun to smoothbore firing. Ammunition is further compatible with the Type 1986 \
100mm high pressure smoothbore anti tank gun, a further development of the former. Cartridges are \
issued with a fixed charge highly specific to each projectile, in copper or combustible casings.\
"

gun_outro = "For simplicity, bundled charge has been treated as the equivalent mass in loose \
grains, and combustible casings have been treated as loose grains of equivalent energy, \
with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).\n\
 《炮弹火箭弹手册：第二分册 陆军炮弹与火箭弹》(1984)"


he_frag_73 = KnownGunProblem(
    name="100mm HE-Frag FS WB031P",
    description="\n".join(
        [
            gun_intro,
            "\
The 100mm Type 71/73 HE-Frag FS (WB031P) is issued with a charge that loads 4.3kg of 20/1 \
tubular grains, bundled in the center. 0.75kg of 14/7 seven perforated loose grains fills the \
the void around the folded fin mechanism, and 0.15kg of 10/1 Rosin Potassium tubular grains are \
loaded as muzzle blast suppressant. \
Nominal velocity is tabulated at 900 m/s. Nominal pressure is <=3000 kgf/cm^2. The adopted \
computational value is 3128 kgf/cm^2.\
",
            gun_outro,
        ]
    ),
    cross_section=0.7854 * dm2,
    shot_mass=15,
    charge_mass=5.2,
    chamber_volume=7.73 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=48.41 * dm,
    propellant=sb_20_1,
    form_function=twenty_one,
).get_gun_developing_pressure(pressure_target=PressureTarget.average_pressure(3128e2 * kgf_dm2))

apfsds_73 = KnownGunProblem(
    name="100mm APFSDS(T) WB125P, Tungsten Cored APFSDS(T) WB132P",
    description="\n".join(
        [
            gun_intro,
            "\
The 100mm steel APFSDS(T) (WB125P) projectiles, and the tungsten cored APFSDS(T) (WB132P) \
proejctiles are issued with a charge that loads 4.6kg of 9/7 seven perforated loose grains, \
with 1.05kg of 18/1 tubular grains bundled in the center. \
Nominal velocity is tabulated at 1505 m/s. Nominal pressure is <=3300 kgf/cm^2. The adopted \
computational value is 3531 kgf/cm^2.\
",
            gun_outro,
        ]
    ),
    cross_section=0.7854 * dm2,
    shot_mass=4.7,
    charge_mass=5.65,
    chamber_volume=8 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.33 * dm,
    propellant=sb_9_7,
    form_function=nine_seven,
).get_gun_developing_pressure(pressure_target=PressureTarget.average_pressure(3531e2 * kgf_dm2))


w_apfsds_86 = KnownGunProblem(
    name="100mm Tungsten APFSDS(T) for Type 86",
    description="\n".join(
        [
            gun_intro,
            "\
The 100mm Tungsten APFSDS(T) round for use on the Type 86 high pressure anti tank gun \
is issued with 0.9kg combustible cartridge casings, of an energetic material (with a propellant \
force of 730,000 kgf-dm/kg), loading 5.79 kg of highly nitrated single based propellant (1,050,000 \
kgf-dm/kg), in loose grains of 19 perforated rosette grains. \
Nominal velocity is tabulated at 1640 m/s. Nominal pressure is 4800 kgf/cm^2 from copper crusher \
gauge, converts to 4643 kgf/cm^2 actual. Note that source reflects preliminary specification, \
the Type 86 as classified adopted a nominal velocity value of 1610 m/s, which is reflected in \
this example. \n\
",
            gun_outro,
        ]
    ),
    cross_section=0.7854 * dm2,
    shot_mass=5.3,
    charge_mass=6.69,
    chamber_volume=8.8 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.89 * dm,
    propellant=gdldjy,
    form_function=fourteen_nineteen,
).get_gun_developing_pressure(pressure_target=PressureTarget.average_pressure(4643e2 * kgf_dm2))


all_guns = [he_frag_73, apfsds_73, w_apfsds_86]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
