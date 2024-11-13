from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from misc import dm3_kg, kg_dm3, kgfdm_kg

df1 = Propellant(
    name="单芳-1",
    description="Values for this propellant is provisional.\n《火炮内弹道计算手册》(1987)",
    density=1.6 * kg_dm3,
    covolume=1.0 * dm3_kg,
    pressure_exponent=0.82,
    force=950000 * kgfdm_kg,
    adiabatic_index=1.24,
)
twentytwo_seven = FormFunction.multi_perf(
    arch_width=mean((2.1, 2.4)),
    perforation_diameter=mean((0.95, 1.2)),
    height=mean((26, 30)),
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)
