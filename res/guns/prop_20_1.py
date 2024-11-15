from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

sb_20_1 = Propellant(
    name="Single Base",
    description="values are notional",
    density=1.6 * kg_dm3,
    force=950000 * kgfdm_kg,
    pressure_exponent=0.82,
    covolume=1.0 * dm3_kg,
    adiabatic_index=1.2,
)

twenty_one = FormFunction.single_perf(arch_width=2, height=408.15)
