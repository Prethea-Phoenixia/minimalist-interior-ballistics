from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

sb_13_7 = Propellant(
    name="Single Base",
    description="2828 K, Nitrated to 204-207.5 mL/g\n\
《火炸药手册 (增订本）第二分册》(1981), 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
    density=1.6 * kg_dm3,
    force=1016400 * kgfdm_kg,
    pressure_exponent=0.84,
    covolume=0.94967 * dm3_kg,
    adiabatic_index=1.2383,
)

thirteen_seven = FormFunction.multi_perf(
    arch_width=mean((1.30, 1.40)),
    perforation_diameter=mean((0.50, 0.70)),
    height=mean((13.0, 15.0)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)
