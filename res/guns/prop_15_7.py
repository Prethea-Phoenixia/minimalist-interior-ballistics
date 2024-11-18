from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

sb_15_7 = Propellant(
    name="Single Base",
    description="values are copied from 13/7 and is nominal.",
    density=1.6 * kg_dm3,
    force=101.64e4 * kgfdm_kg,
    # pressure_exponent=0.84,
    covolume=0.94967 * dm3_kg,
    adiabatic_index=1.2383,
)

fifteen_seven = FormFunction.multi_perf(
    arch_width=1.6,
    perforation_diameter=0.83,
    height=17,
    shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
)
