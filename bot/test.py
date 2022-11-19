import unittest
from main import get_fusion_id_from_filename as gfiff


class TestGalleryNames(unittest.TestCase):

    def test_valid_filenames(self):
        self.assertIsNotNone(gfiff("100.200.png"))
        self.assertIsNotNone(gfiff("182.256-1.png"))
        self.assertIsNotNone(gfiff("299.287_alt.png"))
        self.assertIsNotNone(gfiff("299.287_alt.png"))
        self.assertIsNotNone(gfiff("413.120a.png"))
        self.assertIsNotNone(gfiff("411.367_ALT.png"))

    def test_invalid_filenames(self):
        self.assertIsNone(gfiff("MagikarpSneasel129.215.png"))
        self.assertIsNone(gfiff("CrobatKlinklang_169.337.png"))
        self.assertIsNone(gfiff("Lapras_Cofragrigus_131.362.png"))


if __name__ == '__main__':
    unittest.main()
