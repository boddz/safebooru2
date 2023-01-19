#!/usr/bin/env python3

"""
Here's some examples of what the module is designed for.

Just un-comment the examples that I have put in main to get a feel for it.

I will try to add some more examples in the future, but this should get you
started with the module until I can do that/ create proper docs.
"""


# RequestHandler, Safebooru, Image, Posts, Tags, Comments
from src.safebooru2 import *


def main():
    handler = RequestHandler()
    sb = Safebooru()  # Or you can use the Safebooru object's handler.

    # Download a random post into specified directory.
    # Using `sb.random_id` is slower as it needs response from redirect URL.
    # sb.download(Posts(id=sb.random_id), directory="example/random_posts")

    # Download a specific post, specify name and directory.
    # sb.download(Posts(id=4241904), filename="magica!", directory="example")

    # Download a post using tags query.
    # sb.download(Posts(tags="akemi_homura", limit=5), post_num=3)

    # Find matching tags json data from `Tags` object and print it.
    # Note: this works with following objects: `Tags`, `Posts`, `Comments`.
    # print(sb.json_from(Tags(name="akemi_homura")))

    # Non-json, raw content instead (XML). First 3 tags on default index.
    # print(sb.content_from(Tags(limit=3)))

    # You can do the above stuff more manually if you want, one example here.
    # post = Posts(tags="akemi_homura", limit=5)
    # json = post.fetch_json(handler)[2]
    # dest = post.image_url(json)
    # Image(dest, sb.image_ext(json)).download(handler, directory="example")


if __name__ == "__main__":
    main()
