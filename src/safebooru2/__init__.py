"""
Safebooru Rev: 2
================

Synchronous API wrapper module for safebooru.org implemented in Python3.
"""


from .safebooru import *
from .safebooru import __version__


__all__ = [
    "ImageType",
    "RequestHandler",
    "Image",
    "Posts",
    "Tags",
    "Comments",
    "Safebooru"
]


def _main():
    print(f"Safebooru2 (ver: {__version__})\nUnder contruction...")

    # TODO: an actual argsparse CLI goes here
