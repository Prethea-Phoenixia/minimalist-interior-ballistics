from .test_designs import SingleChargeDesign, MultipleChargeDesign
from minimalist_interior_ballistics.design.fixed_volume_design import FixedVolumeDesign


class TestFixedChargeDesignWithOneCharge(SingleChargeDesign):
    def setUp(self):
        super().setUp()
        self.fvd_BS_3_53_UOF_412 = FixedVolumeDesign.from_base_design(
            base_design=self.base_design, chamber_volume=self.chamber_volume
        )

    def testGetOptimalGun(self):
        self.result = self.fvd_BS_3_53_UOF_412.get_optimal_gun(
            velocity_target=self.velocity_target, pressure_target=self.pressure_target
        )

    def tearDown(self):
        super().tearDown()


class TestFixedChargeDesignWithMultipleCharges(MultipleChargeDesign):
    def setUp(self):
        super().setUp()
        self.fvd_D_44_UO_365K = FixedVolumeDesign.from_base_design(
            base_design=self.base_design, chamber_volume=self.chamber_volume
        )

    def testGetOptimalGun(self):
        self.result = self.fvd_D_44_UO_365K.get_optimal_gun(
            velocity_target=self.velocity_target,
            pressure_target=self.pressure_target,
            charge_mass_ratios=self.charge_masses,
            reduced_burnrate_ratios=self.reduced_burnrate_ratios,
        )
