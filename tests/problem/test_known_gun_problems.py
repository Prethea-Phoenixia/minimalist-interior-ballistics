from ballistics.problem import KnownGunProblem, PressureTarget
from tests.problem.test_problems import MultipleChargeProblem, SingleChargeProblem
from tests import L, dm, dm2, kgf_dm2


class TestKnownGunProblemWithSingleCharge(SingleChargeProblem):
    def setUp(self):
        super().setUp()

    def testKnownGunProblem(self):
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

        self.result = kgp_BS_3_53_UOF_412.get_gun_at_pressure(
            pressure_target=PressureTarget.average_pressure(3070e2 * kgf_dm2)
        )

    def tearDown(self):
        super().tearDown()


class TestKnownGunProblemWithMultipleCharges(MultipleChargeProblem):
    def setUp(self):
        super().setUp()

    def testKnownGunProblem(self):
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

        self.result = kgp_D_44_UO_365K.get_gun_at_pressure(
            reduced_burnrate_ratios=[1 / 14, 1 / 18], pressure_target=PressureTarget.average_pressure(2750e2 * kgf_dm2)
        )

    def tearDown(self):
        super().tearDown()
