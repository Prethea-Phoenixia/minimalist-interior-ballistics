import unittest

from minimalist_interior_ballistics.charge import Propellant
from minimalist_interior_ballistics.form_function import FormFunction, MultiPerfShape
from minimalist_interior_ballistics.gun import Gun
from tests import logger, kgfdm_kg, kg_dm3, dm3_kg, kgf_dm2, L, dm2, dm
from minimalist_interior_ballistics.problem import PressureTarget, BaseProblem


class SingleChargeProblem(unittest.TestCase):
    def setUp(self):
        logger.info(f"test started: {self.id()}")
        NDT_3 = Propellant(
            name="НДТ-3",
            density=1.6 * kg_dm3,
            force=950e3 * kgfdm_kg,
            pressure_exponent=0.81,
            covolume=1.0 * dm3_kg,
            adiabatic_index=1.2,
        )
        eighteen_one_twentysix = FormFunction.single_perf(arch_width=1.8, height=260)
        self.pressure_target = PressureTarget.average_pressure(3070e2 * kgf_dm2)
        self.charge_mass = 5.6
        self.velocity_target = 900
        self.chamber_volume = 7.9 * L
        base_args = {
            "name": "БС-3 52-П-412 53-УОФ-412",
            "cross_section": 0.818 * dm2,
            "shot_mass": 15.6,
            "loss_fraction": 0.03,
            "start_pressure": 30000 * kgf_dm2,
            "travel": 47.38 * dm,
            "form_function": eighteen_one_twentysix,
            "propellant": NDT_3,
        }

        self.base_problem = BaseProblem(**base_args)

    def tearDown(self):
        logger.info(f"test finished: {self.id()}")
        try:
            result: Gun = self.result
            logger.info(f"result: {result.name}\n" + result.to_travel().tabulate())
        except AttributeError:
            logger.info("test did not define a result")
        pass


class MultipleChargeProblem(SingleChargeProblem):

    def setUp(self):
        super().setUp()

        single_base = Propellant(
            name="",
            density=1.6 * kg_dm3,
            force=900e3 * kgfdm_kg,
            pressure_exponent=0.83,
            covolume=1.0 * dm3_kg,
            adiabatic_index=1.2,
        )
        fourteen_seven = FormFunction.multi_perf(
            arch_width=1.4,
            perforation_diameter=0.75,
            height=17,
            shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
        )
        eighteen_one_fourtytwo = FormFunction.single_perf(arch_width=1.8, height=420)
        base_args = {
            "name": "Д-44 УО-365К O-365К",
            "cross_section": 0.582 * dm2,
            "shot_mass": 9.54,
            "loss_fraction": 0.03,
            "start_pressure": 300e2 * kgf_dm2,
            "travel": 35.92 * dm,
            "propellants": [single_base, single_base],
            "form_functions": [fourteen_seven, eighteen_one_fourtytwo],
        }
        self.base_problem = BaseProblem(**base_args)

        self.pressure_target = PressureTarget.average_pressure(2750e2 * kgf_dm2)
        self.charge_masses = [2.34, 0.26]
        self.reduced_burnrate_ratios = [1 / 14, 1 / 18]
        self.velocity_target = 793
        self.chamber_volume = 3.94 * L

    def tearDown(self):
        super().tearDown()


if __name__ == "__main__":
    unittest.main()
