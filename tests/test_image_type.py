from unittest import TestCase

from src import safebooru2


class TestImageType(TestCase):
    def setUp(self):
        self.jpg_val = safebooru2.ImageType.JPG.value

    def test_img_val(self):
        self.assertEqual(self.jpg_val, 'j')

    def test_img_which(self):
        self.assertEqual(safebooru2.ImageType.which('g'), ".gif")

    def test_img_which_error(self):
        """
        Method needs to be in lambda so TypeError is not raised before assert.
        """
        self.assertRaises(ValueError, lambda: safebooru2.ImageType.which('s'))
