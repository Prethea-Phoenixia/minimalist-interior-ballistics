from minimalist_interior_ballistics.problem import KnownGunProblem
from tests.problem.test_problems import MultipleChargeProblem, SingleChargeProblem


class TestKnownGunProblemWithSingleCharge(SingleChargeProblem):
    def setUp(self):
        super().setUp()
        self.kgp_BS_3_53_UOF_412 = KnownGunProblem.from_base_problem(
            base_problem=self.base_problem, chamber_volume=self.chamber_volume, charge_mass=self.charge_mass
        )

    def testKnownGunProblem(self):
        self.result = self.kgp_BS_3_53_UOF_412.get_gun_at_pressure(pressure_target=self.pressure_target)

    def tearDown(self):
        super().tearDown()


class TestKnownGunProblemWithMultipleCharges(MultipleChargeProblem):
    def setUp(self):
        super().setUp()
        self.kgp_D_44_UO_365K = KnownGunProblem.from_base_problem(
            base_problem=self.base_problem, chamber_volume=self.chamber_volume, charge_masses=self.charge_masses
        )

    def testKnownGunProblem(self):
        self.result = self.kgp_D_44_UO_365K.get_gun_at_pressure(
            reduced_burnrate_ratios=self.reduced_burnrate_ratios, pressure_target=self.pressure_target
        )

    def tearDown(self):
        super().tearDown()
