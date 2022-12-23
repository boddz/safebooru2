from unittest import TestCase

from requests import Session
from src import safebooru2


class TestRequestHandler(TestCase):
    def setUp(self):
        self.sb = safebooru2.Safebooru()
        self.post = safebooru2.Posts(id=1038479)
        self.json = self.sb.json_from(self.post)[0]
    
    def test_json_from(self):
        self.assertTrue(type(self.json), dict)
        self.assertTrue("hash" in self.json)

    def test_random_id(self):
        self.assertTrue(type(self.sb.random_id), int)
    
    def test_image_ext(self):
        self.assertEqual(self.sb.image_ext(self.json), "p")
