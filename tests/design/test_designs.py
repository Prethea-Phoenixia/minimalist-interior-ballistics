from tests import SingleChargeTestCase, MultipleChargeTestCase
from minimalist_interior_ballistics.design.base_design import BaseDesign


class SingleChargeDesign(SingleChargeTestCase):
    def setUp(self):
        super().setUp()
        self.base_problem = BaseDesign(**self.base_args)

    def tearDown(self):
        super().tearDown()


class MultipleChargeDesign(MultipleChargeTestCase):
    def setUp(self):
        super().setUp()
        self.base_problem = BaseDesign(**self.base_args)

    def tearDown(self):
        super().tearDown()
