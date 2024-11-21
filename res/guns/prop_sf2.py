from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

sf2 = Propellant(
    name="双芳-2",
    description="2580 K, nitration at 188-193.5 ml/g\n《火炸药手册 (增订本）第二分册》(1981)\
, 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string(
        {
            "Nitrocellulose": 0.56,
            "Nitroglycerin": 0.25,
            "Dinitrotoluene": 0.09,
            "Dibutyl phthalat": 0.06,
            "Ethyl/Methyl Centralite": 0.03,
            "Vaseline": 0.01,
        }
    ),
    density=1.54 * kg_dm3,
    force=96.09e4 * kgfdm_kg,
    covolume=1.04785 * dm3_kg,
    adiabatic_index=1.2706,
)


nineteen_one = FormFunction.single_perf(arch_width=mean((1.88, 1.98)), height=320)
