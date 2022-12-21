from unittest import TestCase

from src import safebooru2


class TestPosts(TestCase):
    def setUp(self):
        self.handler = safebooru2.RequestHandler()
        self.posts = safebooru2.Posts(id=2480127)
        self.url = "https://safebooru.org/index.php?page=dapi&s=post&q=inde" \
                   "x&json=1&limit=100&pid=0&tags=&cid=0&id=2480127"

    def test_posts_url(self):
        self.assertEqual(self.posts.url, self.url)

    def test_posts_json(self):
        self.assertEqual(type(self.posts.fetch_json(self.handler)), list)
        self.assertEqual(type(self.posts.fetch_json(self.handler)[0]), dict)
