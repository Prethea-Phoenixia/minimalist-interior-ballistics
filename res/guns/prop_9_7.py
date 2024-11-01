from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

sb = Propellant(
    name="Single Base",
    description="2811 K, Nitrated to 204-207.5 mL/g\n《火炸药手册 (增订本）第二分册》(1981)\
, 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
    density=1.6 * kg_dm3,
    force=1012200 * kgfdm_kg,
    pressure_exponent=0.83,
    covolume=0.95160 * dm3_kg,
    adiabatic_index=1.2381,
)

nine_seven = FormFunction.multi_perf(
    arch_width=mean((0.95, 1.10)),
    perforation_diameter=mean((0.40, 0.60)),
    height=mean((11.5, 12.6)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)
