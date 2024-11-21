from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

sf3 = Propellant(
    name="双芳-3",
    description="2580 K, nitration at 188-193.5 ml/g\n《火炸药手册 (增订本）第二分册》(1981)\
, 《火炮内弹道计算手册》(1987)\n"
    + format_compo_string(
        {
            "Nitrocellulose": 0.56,
            "Nitroglycerin": 0.265,
            "Dinitrotoluene": 0.09,
            "Dibutyl phthalat": 0.045,
            "Ethyl/Methyl Centralite": 0.03,
            "Vaseline": 0.01,
        }
    ),
    density=1.56 * kg_dm3,
    force=100.14e4 * kgfdm_kg,
    covolume=1.02561 * dm3_kg,
    adiabatic_index=1.2663,
)


twentythree_one = FormFunction.single_perf(arch_width=mean((2.20, 2.35)), height=370)
nineteen_one = FormFunction.single_perf(arch_width=mean((1.90, 1.95)), height=320)
eighteen_one = FormFunction.single_perf(arch_width=mean((1.67, 1.77)), height=260)
sixteen_one = FormFunction.single_perf(arch_width=mean((1.50, 1.63)), height=235)
