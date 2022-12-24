from unittest import TestCase

from requests import Session
from src import safebooru2


class TestRequestHandler(TestCase):
    """
    You will end up getting a ResourceWarning about an unclosed session, you
    can just ignore this.
    """
    def setUp(self):
        self.handler = safebooru2.RequestHandler()
        self.id = 4084270
        self.tags = "akemi_homura"
        self.random_url = "https://safebooru.org/index.php?page=post&s=random"

    def test_handler_user_agent(self):
        self.assertTrue("SafebooruPy/" in self.handler._user_agent)

    def test_handler_headers(self):
        self.assertTrue("User-Agent" in self.handler._headers)

    def test_handler_url_gen(self):
        self.assertEqual(self.random_url,
                         self.handler._url_gen("https://safebooru.org",
                         "index.php?", {"page": "post", "s": "random"}))

    def test_handler_session_type(self):
        self.assertEqual(type(self.handler.session), Session)

    def test_handler_get_request(self):
        self.assertEqual(self.handler.get(self.random_url).status_code, 200)
