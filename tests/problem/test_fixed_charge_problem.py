from minimalist_interior_ballistics.problem import FixedChargeProblem
from tests.problem.test_problems import MultipleChargeProblem, SingleChargeProblem


class TestFixedChargeProblemWithOneCharge(SingleChargeProblem):
    def setUp(self):
        super().setUp()
        self.fcp_BS_3_53_UOF_412 = FixedChargeProblem.from_base_problem(
            base_problem=self.base_problem, charge_mass=self.charge_mass
        )

    def testSolveReducedBurnRateForVolumeAtPressure(self):
        self.result = self.fcp_BS_3_53_UOF_412.solve_reduced_burn_rate_for_volume_at_pressure(
            chamber_volume=self.chamber_volume, pressure_target=self.pressure_target
        )

    def testSolveChamberVolumeAtPressureForVelocity(self):
        self.result, _ = self.fcp_BS_3_53_UOF_412.solve_chamber_volume_at_pressure_for_velocity(
            pressure_target=self.pressure_target, velocity_target=self.velocity_target
        )

    def tearDown(self):
        super().tearDown()


class TestFixedChargeProblemWithMultipleCharges(MultipleChargeProblem):
    def setUp(self):
        super().setUp()
        self.fcp_D_44_UO_365K = FixedChargeProblem.from_base_problem(
            base_problem=self.base_problem, charge_masses=self.charge_masses
        )

    def testSolveReducedBurnRateForVolumeAtPressure(self):
        self.result = self.fcp_D_44_UO_365K.solve_reduced_burn_rate_for_volume_at_pressure(
            reduced_burnrate_ratios=self.reduced_burnrate_ratios,
            chamber_volume=self.chamber_volume,
            pressure_target=self.pressure_target,
        )

    def testSolveChamberVolumeAtPressureForVelocity(self):
        self.result, _ = self.fcp_D_44_UO_365K.solve_chamber_volume_at_pressure_for_velocity(
            reduced_burnrate_ratios=self.reduced_burnrate_ratios,
            pressure_target=self.pressure_target,
            velocity_target=self.velocity_target,
        )

    def tearDown(self):
        super().tearDown()
