from .test_designs import SingleChargeDesign, MultipleChargeDesign
from minimalist_interior_ballistics.design.fixed_charge_design import FixedChargeDesign


class TestFixedChargeDesignWithOneCharge(SingleChargeDesign):
    def setUp(self):
        # self.fcd_BS_3_53_UOF_412 = FixedChargeDesign.from
        super().setUp()

    #
    # def testGetOptimalGun(self):

    def tearDown(self):
        super().tearDown()
