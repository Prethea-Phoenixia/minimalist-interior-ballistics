from statistics import mean

from ballistics.charge import Charge, Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget

from misc import L, dm, dm2, dm3_kg, kg_dm3, kgf_dm2, kgfdm_kg

ndt_3 = Propellant(
    name="НДТ-3",
    density=1.6 * kg_dm3,
    force=960e3,
    pressure_exponent=0.8,
    covolume=1.0 * dm3_kg,
    adiabatic_index=1.2,
)


kgp_D_44_UBR_365 = KnownGunProblem(
    name="Д-44 УБР-365 БР-365",
    description="800 m/s, nominal 2550 kgf/dm^2, blunt-nose, ballistic capped.",
    family="85x629mmR",
    cross_section=0.582 * dm2,
    shot_mass=9.2,
    charge_mass=2.6,
    chamber_volume=3.94 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.92 * dm,
    propellant=ndt_3,
    form_function=FormFunction.single_perf(arch_width=1.4, height=500),
)
D_44_UBR_365 = kgp_D_44_UBR_365.get_gun_developing_pressure(pressure_target=PressureTarget.average_pressure(250e6))

D_44_UO_365K = Gun(
    name="Д-44 УО-365К O-365К",
    description="793 m/s, nominal 2550 kgf/dm^2",
    family="85x629mmR",
    shot_mass=9.54,
    cross_section=0.582 * dm2,
    charges=D_44_UBR_365.charges,
    charge_masses=D_44_UBR_365.charge_masses,
    chamber_volume=3.94 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.92 * dm,
)

ZiS_S_53_D_5_UO_365K = Gun(
    name="ЗИС-С53, Д-5Т85, Д-5С85А, Д-5С85, Д-5СТ85 УО-365К O-365К",
    description="785 m/s, nominal 2550 kgf/dm^2",
    family="85x629mmR",
    shot_mass=9.54,
    charges=D_44_UBR_365.charges,
    charge_masses=[2.53],
    cross_section=0.582 * dm2,
    chamber_volume=3.8 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.92 * dm,
)


ZiS_S_53_D_5_UBR_365K = Gun(
    name="ЗИС-С53, Д-5Т85, Д-5С85А, Д-5С85, Д-5СТ85 УБР-365 БР-365 ",
    description="792 m/s, nominal 2550 kgf/dm^2. blunt-nose, ballistic capped.",
    family="85x629mmR",
    shot_mass=9.2,
    cross_section=0.582 * dm2,
    charges=D_44_UBR_365.charges,
    charge_masses=[2.53],
    chamber_volume=3.8 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.92 * dm,
)


all_guns = [D_44_UO_365K, ZiS_S_53_D_5_UO_365K, D_44_UBR_365, ZiS_S_53_D_5_UBR_365K]

if __name__ == "__main__":
    from ballistics.state import StateList

    for gun in all_guns:
        print(gun.name)
        print(gun.description)
        print(StateList.tabulate(gun.to_travel()))
