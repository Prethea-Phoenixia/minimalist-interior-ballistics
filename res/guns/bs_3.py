from statistics import mean

from ballistics.form_function import FormFunction
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import L, dm, dm2, kgf_dm2
from prop_sf3 import sf3

eighteen_one = FormFunction.single_perf(arch_width=mean((1.67, 1.77)), height=260)
bs_3_he_frag = KnownGunProblem(
    name="Type 1944 100mm Cannon (BS-3) (WB004P HE-Frag)",
    description="Type 1944 100mm cannon is the domestic designation for the Soviet 100mm \
field gun M1944 (BS-3). Nominal velocity is 900m/s. Nominal pressure value is 3000 \
kgf/cm^2, from copper crusher gauge, converts to 3141 kgf/cm^2 actual.\n\
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
    pressure_target=PressureTarget(3141e2 * kgf_dm2, target=PressureTarget.AVERAGE),
)


bs_3_apbc = Gun(
    name="Type 1944 100mm Cannon (BS-3) (WB116P APBC)",
    description="Type 1944 100mm cannon is the domestic designation for the Soviet 100mm \
field gun M1944 (BS-3). Nominal velocity is 902.5m/s. Nominal pressure value is 3000 \
kgf/cm^2, from copper crusher gauge.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.818 * dm2,
    shot_mass=15.88,
    charge_mass=5.6,
    chamber_volume=7.9 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=50.8 * dm,
    charge=bs_3_he_frag.charge,
)

if __name__ == "__main__":
    from ballistics.state import StateList

    print(bs_3_he_frag.chamber_volume)
    print(StateList.tabulate(bs_3_he_frag.to_travel()))

    print(StateList.tabulate(bs_3_apbc.to_travel()))
