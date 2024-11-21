from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

sb_14_7 = Propellant(
    name="Single Base",
    description="2796 K, Nitrated to 204-207.5 mL/g\n\
《火炸药手册 (增订本）第二分册》(1981), 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
    density=1.6 * kg_dm3,
    force=101.13e4 * kgfdm_kg,
    covolume=0.95576 * dm3_kg,
    adiabatic_index=1.2391,
)

# sb_14_7_low = Propellant(
#     name="Single Base (Low Force)",
#     description="2796 K, Nitrated to 204-207.5 mL/g\n\
# 《火炸药手册 (增订本）第二分册》(1981), 《火炮内弹道计算手册》(1987)\n\
# Force adjusted to better reflect older production.\n"
#     + format_compo_string({"Nitrocellulose": 0.985, "Diphenylamin": 0.015}),
#     density=1.6 * kg_dm3,
#     force=sb_14_7.force * 0.9,
#     covolume=0.95576 * dm3_kg,
#     adiabatic_index=1.2391,
# )

fourteen_seven = FormFunction.multi_perf(
    arch_width=mean((1.20, 1.55)),
    perforation_diameter=mean((0.7, 0.8)),
    height=mean((16, 18)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)
