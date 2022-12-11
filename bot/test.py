import unittest
from bot.utils import get_fusion_id_from_filename as gfiff


class TestGalleryNames(unittest.TestCase):

    def test_valid_filenames(self):
        self.assertIsNotNone(gfiff("100.200.png"))
        self.assertIsNotNone(gfiff("413.120c.png"))
        self.assertIsNotNone(gfiff("SPOILER_225.85.png"))
        self.assertIsNotNone(gfiff("SPOILER_355.73a.png"))
        
    def test_invalid_filenames(self):
        self.assertIsNone(gfiff("MagikarpSneasel129.215.png"))
        self.assertIsNone(gfiff("CrobatKlinklang_169.337.png"))
        self.assertIsNone(gfiff("Lapras_Cofragrigus_131.362.png"))
        self.assertIsNone(gfiff("413.120ab.png"))
        self.assertIsNone(gfiff("182.256-1.png"))
        self.assertIsNone(gfiff("138.412.H.png"))
        self.assertIsNone(gfiff("299.287_alt.png"))
        self.assertIsNone(gfiff("411.367_ALT.png"))
        self.assertIsNone(gfiff("299.287.png.png"))
        self.assertIsNone(gfiff("299.287.jpeg"))

if __name__ == '__main__':
    unittest.main()
