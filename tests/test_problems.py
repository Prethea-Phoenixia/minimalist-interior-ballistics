import logging
import unittest
from os import path

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.problem import (FixedChargeProblem, FixedVolumeProblem,
                                KnownGunProblem, PressureTarget)

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

    def testKnownGunProblem(self):
        logger.info("Testing Known Gun Problems")

        kgp_BS_3_53_UOF_412 = KnownGunProblem(
            name="БС-3 52-П-412 53-УОФ-412",
            description="900 m/s",
            cross_section=0.818 * dm2,
            shot_mass=15.6,
            chamber_volume=7.9 * L,
            charge_mass=5.6,
            loss_fraction=0.03,
            start_pressure=30000 * kgf_dm2,
            travel=47.38 * dm,
            propellant=self.NDT_3,
            form_function=self.eighteen_one_twentysix,
        )

        BS_3_53_UOF_412 = kgp_BS_3_53_UOF_412.get_gun_at_pressure(
            pressure_target=PressureTarget.average_pressure(3070e2 * kgf_dm2)
        )
        logger.info(BS_3_53_UOF_412.name)
        logger.info("\n" + BS_3_53_UOF_412.to_travel().tabulate())

        for charge, arch_width in zip(BS_3_53_UOF_412.charges, (1.8e-3,)):
            logger.info(f"{charge.name} {charge.get_coefficient_from_arch(arch_width)} m/s/Pa")

        kgp_D_44_UO_365K = KnownGunProblem(
            name="Д-44 УО-365К O-365К",
            description="793 m/s",
            cross_section=0.582 * dm2,
            shot_mass=9.54,
            charge_masses=[2.34, 0.26],
            chamber_volume=3.94 * L,
            loss_fraction=0.03,
            start_pressure=300e2 * kgf_dm2,
            travel=35.92 * dm,
            propellants=[self.single_base, self.single_base],
            form_functions=[self.fourteen_seven, self.eighteen_one_fourtytwo],
        )

        D_44_UO_365K = kgp_D_44_UO_365K.get_gun_at_pressure(
            reduced_burnrate_ratios=[1 / 14, 1 / 18], pressure_target=PressureTarget.average_pressure(2750e2 * kgf_dm2)
        )

        logger.info(D_44_UO_365K.name)
        logger.info("\n" + D_44_UO_365K.to_travel().tabulate())

        for charge, arch_width in zip(D_44_UO_365K.charges, (1.4e-3, 1.8e-3)):
            logger.info(f"{charge.name} {charge.get_coefficient_from_arch(arch_width)} m/s/Pa")

    def tearDown(self):
        pass


class TestFixedChargeProblem(TestProblems):
    def setUp(self):
        super().setUp()

        self.fcp_BS_3_53_UOF_412 = FixedChargeProblem(
            name="БС-3 52-П-412 53-УОФ-412",
            cross_section=0.818 * dm2,
            shot_mass=15.6,
            charge_mass=5.6,
            loss_fraction=0.03,
            start_pressure=30000 * kgf_dm2,
            travel=47.38 * dm,
            propellant=self.NDT_3,
            form_function=self.eighteen_one_twentysix,
        )

        self.fcp_D_44_UO_365K = FixedChargeProblem(
            name="Д-44 УО-365К O-365К",
            description="793 m/s",
            cross_section=0.582 * dm2,
            shot_mass=9.54,
            loss_fraction=0.03,
            start_pressure=300e2 * kgf_dm2,
            travel=35.92 * dm,
            propellants=[self.single_base, self.single_base],
            form_functions=[self.fourteen_seven, self.eighteen_one_fourtytwo],
            charge_masses=[2.34, 0.26],
        )

    def testSolveReducedBurnRateForVolumeAtPressure(self):
        BS_3_53_UOF_412 = self.fcp_BS_3_53_UOF_412.solve_reduced_burn_rate_for_volume_at_pressure(
            chamber_volume=7.9 * L,
            pressure_target=PressureTarget.average_pressure(3070e2 * kgf_dm2),
        )
        logger.info(BS_3_53_UOF_412.name)
        logger.info("\n" + BS_3_53_UOF_412.to_travel().tabulate())

        for charge, arch_width in zip(BS_3_53_UOF_412.charges, (1.8e-3,)):
            logger.info(f"{charge.name} {charge.get_coefficient_from_arch(arch_width)} m/s/Pa")

    def testSolveChamberVolumeAtPressureForVelocity(self):
        D_44_UO_365K, _ = self.fcp_D_44_UO_365K.solve_chamber_volume_at_pressure_for_velocity(
            reduced_burnrate_ratios=[1 / 14, 1 / 18],
            pressure_target=PressureTarget.average_pressure(2750e2 * kgf_dm2),
            velocity_target=793.0,
        )

        logger.info(D_44_UO_365K.chamber_volume)
        logger.info(D_44_UO_365K.name)
        logger.info("\n" + D_44_UO_365K.to_travel().tabulate())

        for charge, arch_width in zip(D_44_UO_365K.charges, (1.4e-3, 1.8e-3)):
            logger.info(f"{charge.name} {charge.get_coefficient_from_arch(arch_width)} m/s/Pa")

    def tearDown(self):
        super().tearDown()


class TestFixedVolumeProblem(TestProblems):
    def setUp(self):
        super().setUp()

        self.fvp_D_44_UO_365K = FixedVolumeProblem(
            name="Д-44 УО-365К O-365К",
            description="793 m/s",
            cross_section=0.582 * dm2,
            shot_mass=9.54,
            chamber_volume=3.94 * L,
            loss_fraction=0.03,
            start_pressure=300e2 * kgf_dm2,
            travel=35.92 * dm,
            propellants=[self.single_base, self.single_base],
            form_functions=[self.fourteen_seven, self.eighteen_one_fourtytwo],
        )

        self.fvp_BS_3_53_UOF_412 = FixedVolumeProblem(
            name="БС-3 52-П-412 53-УОФ-412",
            description="900 m/s",
            cross_section=0.818 * dm2,
            shot_mass=15.6,
            chamber_volume=7.9 * L,
            loss_fraction=0.03,
            start_pressure=30000 * kgf_dm2,
            travel=47.38 * dm,
            propellant=self.NDT_3,
            form_function=self.eighteen_one_twentysix,
        )

    def testSolveReducedBurnRateForVolumeAtPressure(self):

        BS_3_53_UOF_412 = self.fvp_BS_3_53_UOF_412.solve_reduced_burn_rate_for_charge_at_pressure(
            charge_mass=5.6,
            pressure_target=PressureTarget.average_pressure(3070e2 * kgf_dm2),
        )
        logger.info(BS_3_53_UOF_412.name)
        logger.info("\n" + BS_3_53_UOF_412.to_travel().tabulate())

        for charge, arch_width in zip(BS_3_53_UOF_412.charges, (1.8e-3,)):
            logger.info(f"{charge.name} {charge.get_coefficient_from_arch(arch_width)} m/s/Pa")

    def testSolveChargeMassAtPressureForVelocity(self):
        D_44_UO_365K, _ = self.fvp_D_44_UO_365K.solve_charge_mass_at_pressure_for_velocity(
            velocity_target=793.0,
            pressure_target=PressureTarget.average_pressure(2750e2 * kgf_dm2),
            charge_mass_ratios=[2.34, 0.26],
            reduced_burnrate_ratios=[1 / 14, 1 / 18],
        )

        logger.info(D_44_UO_365K.name)
        logger.info("\n" + D_44_UO_365K.to_travel().tabulate())

        for charge, arch_width in zip(D_44_UO_365K.charges, (1.4e-3, 1.8e-3)):
            logger.info(f"{charge.name} {charge.get_coefficient_from_arch(arch_width)} m/s/Pa")

    def tearDown(self):
        super().tearDown()


if __name__ == "__main__":
    unittest.main()
