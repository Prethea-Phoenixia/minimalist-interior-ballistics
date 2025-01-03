from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

sb_12_7 = Propellant(
    name="Single Base",
    description="2822 K, Nitrated to 204-207.5 mL/g\n\
《火炸药手册 (增订本）第二分册》(1981), 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
    density=1.6 * kg_dm3,
    force=101.51e4 * kgfdm_kg,
    covolume=0.95074 * dm3_kg,
    adiabatic_index=1.2381,
)


# sb_12_7_low = Propellant(
#     name="Single Base (Low Force)",
#     description="2822 K, Nitrated to 204-207.5 mL/g\n\
# 《火炸药手册 (增订本）第二分册》(1981), 《火炮内弹道计算手册》(1987)\n\
# Force adjusted to better reflect older production.\n"
#     + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
#     density=1.6 * kg_dm3,
#     force=sb_12_7.force * 0.9,
#     covolume=0.95074 * dm3_kg,
#     adiabatic_index=1.2381,
# )


twelve_seven = FormFunction.multi_perf(
    arch_width=mean((1.10, 1.30)),
    perforation_diameter=mean((0.50, 0.70)),
    height=mean((13.5, 15.6)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)
