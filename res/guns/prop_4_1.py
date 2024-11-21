from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

sb_4_1 = Propellant(
    name="Single Base",
    description="2923 K, Nitrated to 204-207.5 mL/g\n《火炸药手册 (增订本）第二分册》(1981)\
, 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
    density=1.6 * kg_dm3,
    force=100.321e4 * kgfdm_kg,
    covolume=0.93316 * dm3_kg,
    adiabatic_index=1.2358,
)

four_one = FormFunction.single_perf(arch_width=mean((0.30, 0.55)), height=mean((5.5, 7.5)))
