from .test_designs import SingleChargeDesign, MultipleChargeDesign
from minimalist_interior_ballistics.design.fixed_charge_design import FixedChargeDesign


class TestFixedChargeDesignWithOneCharge(SingleChargeDesign):
    def setUp(self):
        super().setUp()
        self.fcd_BS_3_53_UOF_412 = FixedChargeDesign.from_base_design(
            base_design=self.base_design, charge_mass=self.charge_mass
        )

    def testGetOptimalGun(self):
        self.result = self.fcd_BS_3_53_UOF_412.get_optimal_gun(
            velocity_target=self.velocity_target, pressure_target=self.pressure_target
        )

    def tearDown(self):
        super().tearDown()


class TestFixedChargeDesignWithMultipleCharges(MultipleChargeDesign):
    def setUp(self):
        super().setUp()
        self.fcd_D_44_UO_365K = FixedChargeDesign.from_base_design(
            base_design=self.base_design, charge_masses=self.charge_masses
        )

    def testGetOptimalGun(self):
        self.result = self.fcd_D_44_UO_365K.get_optimal_gun(
            velocity_target=self.velocity_target,
            pressure_target=self.pressure_target,
            reduced_burnrate_ratios=self.reduced_burnrate_ratios,
        )
