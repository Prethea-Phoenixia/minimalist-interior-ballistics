from minimalist_interior_ballistics.problem import FixedVolumeProblem
from tests.problem.test_problems import MultipleChargeProblem, SingleChargeProblem


class TestFixedVolumeProblemWithOneCharge(SingleChargeProblem):
    def setUp(self):
        super().setUp()
        self.fvp_BS_3_53_UOF_412 = FixedVolumeProblem.from_base_problem(
            base_problem=self.base_problem, chamber_volume=self.chamber_volume
        )

    def testSolveReducedBurnRateForVolumeAtPressure(self):
        self.result = self.fvp_BS_3_53_UOF_412.solve_reduced_burn_rate_for_charge_at_pressure(
            charge_mass=self.charge_mass, pressure_target=self.pressure_target
        )

    def testSolveChargeMassAtPressureForVelocity(self):
        self.result, _ = self.fvp_BS_3_53_UOF_412.solve_charge_mass_at_pressure_for_velocity(
            velocity_target=self.velocity_target, pressure_target=self.pressure_target
        )

    def tearDown(self):
        super().tearDown()


class TestFixedVolumeProblemWithMultipleCharges(MultipleChargeProblem):
    def setUp(self):
        super().setUp()
        self.fvp_D_44_UO_365K = FixedVolumeProblem.from_base_problem(
            base_problem=self.base_problem, chamber_volume=self.chamber_volume
        )

    def testSolveReducedBurnRateForChargeAtPressure(self):
        self.result = self.fvp_D_44_UO_365K.solve_reduced_burn_rate_for_charge_at_pressure(
            pressure_target=self.pressure_target,
            charge_masses=self.charge_masses,
            reduced_burnrate_ratios=self.reduced_burnrate_ratios,
        )

    def testSolveChargeMassAtPressureForVelocity(self):
        self.result, _ = self.fvp_D_44_UO_365K.solve_charge_mass_at_pressure_for_velocity(
            velocity_target=self.velocity_target,
            pressure_target=self.pressure_target,
            charge_mass_ratios=self.charge_masses,
            reduced_burnrate_ratios=self.reduced_burnrate_ratios,
        )

    def tearDown(self):
        super().tearDown()
