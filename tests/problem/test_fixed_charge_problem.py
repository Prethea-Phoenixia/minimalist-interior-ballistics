from ballistics.problem import FixedChargeProblem, PressureTarget
from tests.problem.test_problems import MultipleChargeProblem, SingleChargeProblem
from tests import L, dm, dm2, kgf_dm2


class TestFixedChargeProblemWithOneCharge(SingleChargeProblem):
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

    def testSolveReducedBurnRateForVolumeAtPressure(self):
        self.result = self.fcp_BS_3_53_UOF_412.solve_reduced_burn_rate_for_volume_at_pressure(
            chamber_volume=7.9 * L,
            pressure_target=PressureTarget.average_pressure(3070e2 * kgf_dm2),
        )

    def testSolveChamberVolumeAtPressureForVelocity(self):
        self.result, _ = self.fcp_BS_3_53_UOF_412.solve_chamber_volume_at_pressure_for_velocity(
            pressure_target=PressureTarget.average_pressure(3070e2 * kgf_dm2),
            velocity_target=900.0,
        )

    def tearDown(self):
        super().tearDown()


class TestFixedChargeProblemWithMultipleCharges(MultipleChargeProblem):
    def setUp(self):
        super().setUp()
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
        self.result = self.fcp_D_44_UO_365K.solve_reduced_burn_rate_for_volume_at_pressure(
            reduced_burnrate_ratios=[1 / 14, 1 / 18],
            chamber_volume=3.94 * L,
            pressure_target=PressureTarget.average_pressure(2750e2 * kgf_dm2),
        )

    def testSolveChamberVolumeAtPressureForVelocity(self):
        self.result, _ = self.fcp_D_44_UO_365K.solve_chamber_volume_at_pressure_for_velocity(
            reduced_burnrate_ratios=[1 / 14, 1 / 18],
            pressure_target=PressureTarget.average_pressure(2750e2 * kgf_dm2),
            velocity_target=793.0,
        )

    def tearDown(self):
        super().tearDown()
