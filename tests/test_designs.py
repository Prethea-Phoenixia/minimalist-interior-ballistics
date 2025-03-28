import logging
import unittest
from os import path

from ballistics.charge import Propellant
from ballistics.design import FixedChargeDesign
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.problem import PressureTarget

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    filename=f"{path.splitext(__file__)[0]}.log",
    format="[%(asctime)s] [%(levelname)8s] %(message)s",  # (%(filename)s:%(lineno)s),
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="w+",
)

dm = 1e-1
dm2 = 1e-2
L = 1e-3
kg_dm3 = 1e3
dm3_kg = 1e-3
kgfdm_kg = 0.98
kgf_dm2 = 980
dm_s = 0.1


class TestProblems(unittest.TestCase):
    """
    values in the test case are notional to verify correctness of program.
    """

    def setUp(self):
        logger.info("Started")

        self.NDT_3 = Propellant(
            name="НДТ-3",
            density=1.6 * kg_dm3,
            force=950e3 * kgfdm_kg,
            pressure_exponent=0.81,
            covolume=1.0 * dm3_kg,
            adiabatic_index=1.2,
        )
        self.eighteen_one_twentysix = FormFunction.single_perf(arch_width=1.8, height=260)

        self.single_base = Propellant(
            name="",
            density=1.6 * kg_dm3,
            force=900e3 * kgfdm_kg,
            pressure_exponent=0.83,
            covolume=1.0 * dm3_kg,
            adiabatic_index=1.2,
        )

        self.fourteen_seven = FormFunction.multi_perf(
            arch_width=1.4,
            perforation_diameter=0.75,
            height=17,
            shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
        )

        self.eighteen_one_fourtytwo = FormFunction.single_perf(arch_width=1.8, height=420)

    def testFixedChargeDesigns(self):
        logger.info("Testing Fixed Charge Designs")
        """53-УОФ-412 with НДТ-3 18/1"""

        fcd_BS_3_53_UOF_412 = FixedChargeDesign(
            name="БС-3 52-П-412 53-УОФ-412",
            cross_section=0.818 * dm2,
            shot_mass=15.6,
            charge_mass=5.6,
            loss_fraction=0.03,
            start_pressure=30000 * kgf_dm2,
            pressure_target=PressureTarget.average_pressure(3070e2 * kgf_dm2),
            propellant=self.NDT_3,
            form_function=self.eighteen_one_twentysix,
        )

        BS_3_53_UOF_412 = fcd_BS_3_53_UOF_412.get_optimal_gun(
            velocity_target=900,
        )
        logger.info(BS_3_53_UOF_412.name)
        logger.info("\n" + BS_3_53_UOF_412.to_travel().tabulate())

        for charge, arch_width in zip(BS_3_53_UOF_412.charges, (1.8e-3,)):
            logger.info(f"{charge.name} {charge.get_coefficient_from_arch(arch_width)} m/s/Pa")

    def tearDown(self):
        logger.info("Ended")


if __name__ == "__main__":
    unittest.main()
