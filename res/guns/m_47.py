from statistics import mean

from ballistics.form_function import FormFunction
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_sf3 import sf3

nineteen_one = FormFunction.single_perf(arch_width=mean((1.90, 1.95)), height=320)
m_47_full = KnownGunProblem(
    name="Type 1959 152mm Cannon (M-47) (WB008P HE-Frag, Full Charge)",
    description="Type 1959 152mm cannon is the designation for domestically produced \
variants of the Soviet 152mm towed field gun M1954 (M-47). The Full Variable charge is \
made up of various charge bags that adds up to 8.45kg. Further supplementary charge bags\
bring the full charge to 10.67 kg. Nominal velocity is 770 m/s. Peak pressure converted\
from copper crusher value, nominally 235,000 kgf/dm^2. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.876 * dm2,
    shot_mass=43.56,
    charge_mass=10.67,
    chamber_volume=17.27 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=55.77 * dm,
    propellant=sf3,
    form_function=nineteen_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(2570e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)

m_47_one = Gun(
    name="Type 1959 152mm Cannon (M-47) (WB008P HE-Frag, No.1 Charge)",
    description="Type 1959 152mm cannon is the designation for domestically produced \
variants of the Soviet 152mm towed field gun M1954 (M-47). The Full Variable charge is \
made up of various charge bags that adds up to 8.45kg. Further supplementary charge bags\
bring the full charge to 10.67 kg. Nominal velocity is 635 m/s.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=1.876 * dm2,
    shot_mass=43.56,
    charge_mass=8.45,
    chamber_volume=19.25 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=55.77 * dm,
    charge=m_47_full.charge,
)

if __name__ == "__main__":
    from ballistics.state import StateList

    print(StateList.tabulate(m_47_full.to_travel(n_intg=10)))
    print(StateList.tabulate(m_47_one.to_travel(n_intg=10)))
