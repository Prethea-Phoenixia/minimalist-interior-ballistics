import logging
import unittest

from ballistics.charge import Charge, Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.gun import Gun
from ballistics.problem import (FixedChargeProblem, FixedVolumeProblem,
                                PressureTarget)
from ballistics.state import State, StateList

from units import L, dm, dm2, dm3_kg, kg_dm3, kgf_dm2, kgfdm_kg

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    filename="test_known_gun_problem.log",
    format="[%(asctime)s] [%(levelname)8s] %(message)s",  # (%(filename)s:%(lineno)s),
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="w+",
)


class TestFixedChargeProblem(unittest.TestCase):

    def setUp(self):
        logger.info("Started")

        self.NDT_3 = Propellant(
            name="НДТ-3",
            description="",
            density=1.6 * kg_dm3,
            force=950e3 * kgfdm_kg,
            pressure_exponent=0.81,
            covolume=1.0 * dm3_kg,
            adiabatic_index=1.2,
        )
        self.eighteen_one = FormFunction.single_perf(arch_width=0.85 * 2, height=260)

    def testMonoPropCase(self):
        """53-УОФ-412 with НДТ-3 18/1"""

        fcp_BS_3_53_UOF_412 = FixedChargeProblem(
            name="БС-3 52-П-412 53-УОФ-412",
            cross_section=0.818 * dm2,
            shot_mass=15.6,
            charge_mass=5.6,
            loss_fraction=0.03,
            start_pressure=30000 * kgf_dm2,
            travel=47.38 * dm,
            propellant=self.NDT_3,
            form_function=self.eighteen_one,
        )

        BS_3_53_UOF_412 = fcp_BS_3_53_UOF_412.solve_reduced_burn_rate_for_volume_at_pressure(
            chamber_volume=7.9 * L,
            pressure_target=PressureTarget.average_pressure(3000e2 * kgf_dm2),
            n_intg=100,
            acc=1e-3,
        )
        logger.info(BS_3_53_UOF_412)
        logger.info(BS_3_53_UOF_412.velocity_limit)
        logger.info("\n" + BS_3_53_UOF_412.to_travel().tabulate())

    def tearDown(self):
        logger.info("Ended")


if __name__ == "__main__":
    unittest.main()
