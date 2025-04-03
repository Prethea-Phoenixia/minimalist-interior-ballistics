from idlelib.configdialog import changes

from minimalist_interior_ballistics.gun import Gun
from minimalist_interior_ballistics.problem import FixedVolumeProblem, PressureTarget
from tests.problem.test_problems import MultipleChargeProblem, SingleChargeProblem
from tests import L, dm, dm2, kgf_dm2, logger


class TestFixedVolumeProblemWithOneCharge(SingleChargeProblem):
    def setUp(self):
        super().setUp()
        self.fvp_BS_3_53_UOF_412 = FixedVolumeProblem(
            **self.base_args,
            chamber_volume=self.chamber_volume,
            propellant=self.NDT_3,
            form_function=self.eighteen_one_twentysix,
        )

    def testChargeMassLimits(self):
        def f(cm: float) -> Gun:
            return self.fvp_BS_3_53_UOF_412.get_gun_at_pressure(pressure_target=self.pressure_target, charge_mass=cm)

        guns = [f(cm) for cm in self.fvp_BS_3_53_UOF_412.get_charge_mass_limits(pressure_target=self.pressure_target)]

        logger.info(
            "corresponding reduced burn rates (m/s/Pa^n):"
            + " ".join((f"{gun.gross_charge_mass:.1f} kg @ {gun.charges[0].reduced_burnrate:.3e}") for gun in guns)
        )

    def testSolveReducedBurnRateForVolumeAtPressure(self):
        result = self.fvp_BS_3_53_UOF_412.solve_reduced_burn_rate_for_charge_at_pressure(
            charge_mass=self.charge_mass, pressure_target=self.pressure_target
        )

    def testSolveChargeMassAtPressureForVelocity(self):
        result, _ = self.fvp_BS_3_53_UOF_412.solve_charge_mass_at_pressure_for_velocity(
            velocity_target=self.velocity_target, pressure_target=self.pressure_target
        )

    def tearDown(self):
        super().tearDown()


class TestFixedVolumeProblemWithMultipleCharges(MultipleChargeProblem):
    def setUp(self):
        super().setUp()
        self.fvp_D_44_UO_365K = FixedVolumeProblem(
            **self.base_args,
            chamber_volume=self.chamber_volume,
            propellants=[self.single_base, self.single_base],
            form_functions=[self.fourteen_seven, self.eighteen_one_fourtytwo],
        )

    def testSolveReducedBurnRateForChargeAtPressure(self):
        result = self.fvp_D_44_UO_365K.solve_reduced_burn_rate_for_charge_at_pressure(
            pressure_target=self.pressure_target,
            charge_masses=self.charge_masses,
            reduced_burnrate_ratios=self.reduced_burnrate_ratios,
        )

    def testSolveChargeMassAtPressureForVelocity(self):
        result, _ = self.fvp_D_44_UO_365K.solve_charge_mass_at_pressure_for_velocity(
            velocity_target=self.velocity_target,
            pressure_target=self.pressure_target,
            charge_mass_ratios=self.charge_masses,
            reduced_burnrate_ratios=self.reduced_burnrate_ratios,
        )

    def tearDown(self):
        super().tearDown()
