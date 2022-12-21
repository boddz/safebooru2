from unittest import TestCase

from src import safebooru2


class TestImage(TestCase):
    def setUp(self):
        self.img_dest = "https://safebooru.org//samples/3466/sample_05ab774" \
                        "69b43f563c3745cbb53a57ca7d2fc6869.jpg?3605424"
        self.image = safebooru2.Image(self.img_dest, "j")

    def test_image_file_name(self):
        self.assertEqual(self.image.file_name, "3605424.jpg")
