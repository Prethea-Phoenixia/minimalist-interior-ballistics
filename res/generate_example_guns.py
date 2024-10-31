import logging
from typing import Dict

from ballistics.charge import Charge, Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.gun import Gun
from ballistics.problem import (FixedChargeProblem, FixedVolumeProblem,
                                PressureTarget)
from ballistics.state import State, StateList

logger = logging.getLogger(__name__)
dm = 1e-1
dm2 = 1e-2
L = 1e-3
kg_dm3 = 1e3
dm3_kg = 1e-3
kgfdm_kg = 0.98
kgf_dm2 = 980
dm_s = 0.1


def format_compo_string(compo_dict: Dict[str, float]) -> str:
    return (
        "\n".join(
            f"{percentage:>3.1%} {ingredient}" for ingredient, percentage in compo_dict.items()
        )
        + "\n"
    )


if __name__ in {"__main__", "__mp_main__"}:
    logging.basicConfig(
        level=logging.INFO,
        # filename="example.log",
        format="[%(asctime)s] [%(levelname)8s] %(message)s",  # (%(filename)s:%(lineno)s),
        datefmt="%Y-%m-%d %H:%M:%S",
        # filemode="w+",
    )
    logger.info("Started")

    sf3 = Propellant(
        name="双芳-3",
        description="2580 K, lit. 'Double Aromatic -3'\n《火炸药手册 (增订本）第二分册》(1981)\
, 《火炮内弹道计算手册》(1987)\n"
        + format_compo_string(
            {
                "Nitrocellulose": 0.56,
                "Nitroglycerin": 0.265,
                "2,4-Dinitrotoluene": 0.09,
                "Dibutyl phthalat": 0.045,
                "Ethyl/Methyl Centralite": 0.03,
                "Vaseline": 0.01,
            }
        ),
        density=1.6 * kg_dm3,
        force=1001e3 * kgfdm_kg,
        pressure_exponent=0.81,
        covolume=1.0 * dm3_kg,
        adiabatic_index=1.2,
    )

    #     sf3 = Propellant(
    #         name="双芳-3",
    #         description="2580 K, lit. 'Double Aromatic -3'\n《火炸药手册 (增订本）第二分册》(1981)\
    # , 《火炮内弹道计算手册》(1987)\n"
    #         + format_compo_string(
    #             {
    #                 "Nitrocellulose": 0.56,
    #                 "Nitroglycerin": 0.265,
    #                 "2,4-Dinitrotoluene": 0.09,
    #                 "Dibutyl phthalat": 0.045,
    #                 "Ethyl/Methyl Centralite": 0.03,
    #                 "Vaseline": 0.01,
    #             }
    #         ),
    #         density=1.6 * kg_dm3,
    #         force=100e3 * kgfdm_kg,
    #         pressure_exponent=0.81,
    #         covolume=1.0 * dm3_kg,
    #         adiabatic_index=1.2,
    #     )

    logger.info("Defined Propellants")

    eighteen_one = FormFunction.single_perf(arch_width=0.85 * 2, height=260)
    type_1944_100 = FixedChargeProblem(
        name="Type 1944 100mm Cannon (WB004P HE-Frag)",
        description="Type 1944 100mm cannon is the domestic designation for the Soviet 100mm \
field gun M1944 (BS-3).\nReference:\n 《火炮内弹道计算手册》(1987)\n 《火炸药手册 (增订本）第二分册》\
(1981).",
        cross_section=0.818 * dm2,
        shot_mass=15.6,
        charge_mass=5.6,
        loss_fraction=0.03,
        start_pressure=300e2 * kgf_dm2,
        travel=47.38 * dm,
        propellant=sf3,
        form_function=eighteen_one,
    ).solve_reduced_burn_rate_for_volume_at_pressure(
        chamber_volume=7.9 * L,
        pressure_target=PressureTarget(3000e2 * kgf_dm2, target=PressureTarget.AVERAGE),
        n_intg=100,
        acc=1e-3,
    )

    logger.info("Solved Gun Problems")

    print(type_1944_100)

    print(StateList.tabulate(type_1944_100.to_travel(n_intg=100, acc=1e-3)))

    Gun.to_file(guns=[type_1944_100], filename="example_guns.json")
    logger.info("end")
