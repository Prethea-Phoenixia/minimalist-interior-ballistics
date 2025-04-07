from tests import SingleChargeTestCase, MultipleChargeTestCase
from minimalist_interior_ballistics.problem import BaseProblem


class SingleChargeProblem(SingleChargeTestCase):
    def setUp(self):
        super().setUp()
        self.base_problem = BaseProblem(**self.base_args, travel=self.travel)

    def tearDown(self):
        super().tearDown()


class MultipleChargeProblem(MultipleChargeTestCase):
    def setUp(self):
        super().setUp()
        self.base_problem = BaseProblem(**self.base_args, travel=self.travel)

    def tearDown(self):
        super().tearDown()
