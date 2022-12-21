from unittest import TestCase

from src import safebooru


class TestPosts(TestCase):
    def setUp(self):
        self.posts = safebooru.Posts(id=2480127)
        self.url = "https://safebooru.org/index.php?page=dapi&s=post&q=inde" \
                   "x&json=1&limit=100&pid=0&tags=&cid=0&id=2480127"

    def test_image_file_name(self):
        self.assertEqual(self.posts.url, self.url)
