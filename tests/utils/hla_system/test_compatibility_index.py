import unittest

from kidney_exchange.utils.hla_system.compatibility_index import compatibility_index
from tests.patients.test_patient_parameters import donor_parameters_Joe, recipient_parameters_Jack


class TestCompatibilityIndex(unittest.TestCase):
    def setUp(self):
        self._donor_recipient_index = [(donor_parameters_Joe, recipient_parameters_Jack, 21.0)]

    def test_compatibility_index(self):
        print("[INFO] Testing compatibility index")
        for donor_params, recipient_params, expected_compatibility_index in self._donor_recipient_index:
            calculated_compatibility_index = compatibility_index(donor_params, recipient_params)
            self.assertEqual(calculated_compatibility_index, expected_compatibility_index)
        print("    -- done\n")