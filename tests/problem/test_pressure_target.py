from unittest import TestCase
from minimalist_interior_ballistics.problem import PressureTarget


class TestPressureTarget(TestCase):
    def setUp(self):
        pass

    def testTargetValidator(self):
        with self.assertRaises(ValueError):
            PressureTarget(target="Test", value=1)

    def tearDown(self):
        pass
