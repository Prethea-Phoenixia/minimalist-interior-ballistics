from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

yf3 = Propellant(
    name="乙芳-3",
    description="2504 K, nitration at 188-193.5 ml/g\n\
《火炸药手册 (增订本）第二分册》(1981), 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string(
        {
            "Nitrocellulose": 0.625,
            "Diethylene Glycol Dinitrate": 0.295,
            "Dinitrotoluene": 0.04,
            "Ethyl/Methyl Centralite": 0.03,
            "Vaseline": 0.01,
        }
    ),
    density=1.6 * kg_dm3,
    force=986600 * kgfdm_kg,
    pressure_exponent=0.81,
    covolume=1.04117 * dm3_kg,
    adiabatic_index=1.2633,
)
seventeen_one = FormFunction.single_perf(arch_width=mean((1.70, 1.80)), height=225)
