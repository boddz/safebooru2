from unittest import TestCase

from src import safebooru2


class TestPosts(TestCase):
    """
    You will end up getting a ResourceWarning about an unclosed session, you
    can just ignore this.
    """
    def setUp(self):
        self.handler = safebooru2.RequestHandler()
        self.comms = safebooru2.Comments(post_id=4084270)
        self.url = "https://safebooru.org/index.php?page=dapi&s=comment&q=i" \
                   "ndex&post_id=4084270"

    def test_comments_url(self):
        self.assertEqual(self.comms.url, self.url)

    def test_comments_json(self):
        self.assertTrue("comments" in self.comms.fetch_json(self.handler))
        self.assertEqual(type(self.comms.fetch_json(self.handler)), dict)
