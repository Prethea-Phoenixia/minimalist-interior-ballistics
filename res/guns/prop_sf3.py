from ballistics.charge import Propellant
from misc import dm3_kg, format_compo_string, kg_dm3, kgfdm_kg

sf3 = Propellant(
    name="双芳-3",
    description="2580 K\n《火炸药手册 (增订本）第二分册》(1981)\
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
    force=1001400 * kgfdm_kg,
    pressure_exponent=0.81,
    covolume=1.02561 * dm3_kg,
    adiabatic_index=1.2663,
)