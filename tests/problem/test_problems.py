import unittest

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from tests import logger, kgfdm_kg, kg_dm3, dm3_kg


class SingleChargeProblem(unittest.TestCase):
    def setUp(self):
        self.NDT_3 = Propellant(
            name="НДТ-3",
            density=1.6 * kg_dm3,
            force=950e3 * kgfdm_kg,
            pressure_exponent=0.81,
            covolume=1.0 * dm3_kg,
            adiabatic_index=1.2,
        )
        self.eighteen_one_twentysix = FormFunction.single_perf(arch_width=1.8, height=260)

    def tearDown(self):

        logger.info(self.result.name)
        logger.info("\n" + self.result.to_travel().tabulate())


class MultipleChargeProblem(SingleChargeProblem):

    def setUp(self):
        super().setUp()

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

    def tearDown(self):
        super().tearDown()


if __name__ == "__main__":
    unittest.main()
