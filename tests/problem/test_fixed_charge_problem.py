from minimalist_interior_ballistics.gun import Gun
from minimalist_interior_ballistics.problem import FixedChargeProblem, PressureTarget
from tests.problem.test_problems import MultipleChargeProblem, SingleChargeProblem
from tests import L, dm, dm2, kgf_dm2
from tests import logger


class TestFixedChargeProblemWithOneCharge(SingleChargeProblem):
    def setUp(self):
        super().setUp()
        self.fcp_BS_3_53_UOF_412 = FixedChargeProblem(
            **self.base_args,
            charge_mass=self.charge_mass,
            propellant=self.NDT_3,
            form_function=self.eighteen_one_twentysix,
        )

    def testGetChamberVolumeLimits(self):
        def f(cv: float) -> Gun:
            return self.fcp_BS_3_53_UOF_412.get_gun_at_pressure(pressure_target=self.pressure_target, chamber_volume=cv)

        guns = [
            f(cv) for cv in self.fcp_BS_3_53_UOF_412.get_chamber_volume_limits(pressure_target=self.pressure_target)
        ]
        logger.info(
            "corresponding reduced burn rates (m/s/Pa^n):"
            + " ".join((f"{gun.chamber_volume*1e3:.1f}L @ {gun.charges[0].reduced_burnrate:.3e}") for gun in guns)
        )

    def testSolveReducedBurnRateForVolumeAtPressure(self):
        result = self.fcp_BS_3_53_UOF_412.solve_reduced_burn_rate_for_volume_at_pressure(
            chamber_volume=self.chamber_volume, pressure_target=self.pressure_target
        )

    def testSolveChamberVolumeAtPressureForVelocity(self):
        result, _ = self.fcp_BS_3_53_UOF_412.solve_chamber_volume_at_pressure_for_velocity(
            pressure_target=self.pressure_target, velocity_target=self.velocity_target
        )

    def tearDown(self):
        super().tearDown()


class TestFixedChargeProblemWithMultipleCharges(MultipleChargeProblem):
    def setUp(self):
        super().setUp()
        self.fcp_D_44_UO_365K = FixedChargeProblem(
            **self.base_args,
            propellants=[self.single_base, self.single_base],
            form_functions=[self.fourteen_seven, self.eighteen_one_fourtytwo],
            charge_masses=self.charge_masses,
        )

    def testSolveReducedBurnRateForVolumeAtPressure(self):
        result = self.fcp_D_44_UO_365K.solve_reduced_burn_rate_for_volume_at_pressure(
            reduced_burnrate_ratios=self.reduced_burnrate_ratios,
            chamber_volume=self.chamber_volume,
            pressure_target=self.pressure_target,
        )

    def testSolveChamberVolumeAtPressureForVelocity(self):
        result, _ = self.fcp_D_44_UO_365K.solve_chamber_volume_at_pressure_for_velocity(
            reduced_burnrate_ratios=self.reduced_burnrate_ratios,
            pressure_target=self.pressure_target,
            velocity_target=self.velocity_target,
        )

    def tearDown(self):
        super().tearDown()
