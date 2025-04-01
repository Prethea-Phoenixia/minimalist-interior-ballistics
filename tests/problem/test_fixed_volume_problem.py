from ballistics.problem import FixedVolumeProblem, PressureTarget
from tests.problem.test_problems import MultipleChargeProblem, SingleChargeProblem
from tests import L, dm, dm2, kgf_dm2


class TestFixedVolumeProblemWithOneCharge(SingleChargeProblem):
    def setUp(self):
        super().setUp()
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
        self.result = self.fvp_BS_3_53_UOF_412.solve_reduced_burn_rate_for_charge_at_pressure(
            charge_mass=5.6, pressure_target=PressureTarget.average_pressure(3070e2 * kgf_dm2)
        )

    def testSolveChargeMassAtPressureForVelocity(self):
        self.result, _ = self.fvp_BS_3_53_UOF_412.solve_charge_mass_at_pressure_for_velocity(
            velocity_target=900, pressure_target=PressureTarget.average_pressure(3070e2 * kgf_dm2)
        )

    def tearDown(self):
        super().tearDown()


class TestFixedVolumeProblemWithMultipleCharges(MultipleChargeProblem):
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

    def testSolveReducedBurnRateForChargeAtPressure(self):
        self.result = self.fvp_D_44_UO_365K.solve_reduced_burn_rate_for_charge_at_pressure(
            pressure_target=PressureTarget.average_pressure(2750e2 * kgf_dm2),
            charge_masses=[2.34, 0.26],
            reduced_burnrate_ratios=[1 / 14, 1 / 18],
        )

    def testSolveChargeMassAtPressureForVelocity(self):
        self.result, _ = self.fvp_D_44_UO_365K.solve_charge_mass_at_pressure_for_velocity(
            velocity_target=793.0,
            pressure_target=PressureTarget.average_pressure(2750e2 * kgf_dm2),
            charge_mass_ratios=[2.34, 0.26],
            reduced_burnrate_ratios=[1 / 14, 1 / 18],
        )

    def tearDown(self):
        super().tearDown()
