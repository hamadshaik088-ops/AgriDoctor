import unittest

from services.treatment_service import get_treatments_for_disease


class TreatmentServiceTest(unittest.TestCase):
    def test_known_crop_disease_has_crop_specific_options(self):
        treatments = get_treatments_for_disease("Tomato", "Early blight")

        self.assertTrue(treatments)
        self.assertTrue(all(item["crop"] == "Tomato" for item in treatments))
        self.assertTrue(all(item["disease"] == "Early blight" for item in treatments))

    def test_unknown_disease_has_no_unsafe_generic_option(self):
        self.assertEqual(get_treatments_for_disease("Rice", "Unknown disease"), [])

    def test_viral_disease_has_no_pesticide_recommendation(self):
        self.assertEqual(get_treatments_for_disease("Tomato", "Tomato mosaic virus"), [])


if __name__ == "__main__":
    unittest.main()