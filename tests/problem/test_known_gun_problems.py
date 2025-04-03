from minimalist_interior_ballistics.problem import KnownGunProblem, PressureTarget
from tests.problem.test_problems import MultipleChargeProblem, SingleChargeProblem
from tests import L, dm, dm2, kgf_dm2


class TestKnownGunProblemWithSingleCharge(SingleChargeProblem):
    def setUp(self):
        super().setUp()

    def testKnownGunProblem(self):
        kgp_BS_3_53_UOF_412 = KnownGunProblem(
            **self.base_args,
            chamber_volume=self.chamber_volume,
            charge_mass=self.charge_mass,
            propellant=self.NDT_3,
            form_function=self.eighteen_one_twentysix,
        )
        kgp_BS_3_53_UOF_412.get_gun_at_pressure(pressure_target=self.pressure_target)

    def tearDown(self):
        super().tearDown()


class TestKnownGunProblemWithMultipleCharges(MultipleChargeProblem):
    def setUp(self):
        super().setUp()

    def testKnownGunProblem(self):
        kgp_D_44_UO_365K = KnownGunProblem(
            **self.base_args,
            charge_masses=self.charge_masses,
            chamber_volume=self.chamber_volume,
            propellants=[self.single_base, self.single_base],
            form_functions=[self.fourteen_seven, self.eighteen_one_fourtytwo],
        )

        kgp_D_44_UO_365K.get_gun_at_pressure(
            reduced_burnrate_ratios=self.reduced_burnrate_ratios, pressure_target=self.pressure_target
        )

    def tearDown(self):
        super().tearDown()
