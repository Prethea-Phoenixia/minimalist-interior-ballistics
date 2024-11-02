from statistics import mean

from ballistics.form_function import FormFunction
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_sf3 import sf3

eighteen_one = FormFunction.single_perf(arch_width=mean((1.67, 1.77)), height=260)
bs_3 = KnownGunProblem(
    name="Type 1944 100mm Cannon (BS-3) (WB004P HE-Frag)",
    description="Type 1944 100mm cannon is the domestic designation for the Soviet 100mm \
field gun M1944 (BS-3). Nominal velocity is 900m/s. Pressure values are converted from \
copper crusher gauge values, nominally 300,000 kgf/dm^2.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.818 * dm2,
    shot_mass=15.6,
    charge_mass=5.6,
    chamber_volume=7.9 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=47.38 * dm,
    propellant=sf3,
    form_function=eighteen_one,
).get_gun_developing_pressure(
    pressure_target=PressureTarget(3202e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)


if __name__ == "__main__":
    from ballistics.state import StateList

    print(bs_3.chamber_volume)
    print(StateList.tabulate(bs_3.to_travel(n_intg=10)))
