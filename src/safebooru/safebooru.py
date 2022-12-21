#!/usr/bin/env python3

"""
A module containing classes and methods for interacting with the safebooru.org
public API. This is my second API wrapper module for safebooru.org, here's the
link to that: <https://github.com/boddz/safebooru> it is one of my older
projects, some things are poorly done, and I am bored so that's why this
module is a thing.

For some more information about the safebooru.org API, you can find some
official documentation: <https://safebooru.org/index.php?page=help&topic=dapi>

As safebooru.org is running a variant of Gelbooru, you can find a bit more
documentation at: <https://gelbooru.com/index.php?page=wiki&s=view&id=18780>
Other parts of gelbooru.com are NSFW, so heads up.

To be released under the GNU GPLv3 licence, which can be found in the source
directory, or with this link: <https://www.gnu.org/licenses/gpl-3.0.en.html>
"""

#region (imports)

from enum import Enum, unique
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from platform import uname

import requests
import xmltodict
from requests import Session

#endregion

#region (global variables)

__version__ = "v1.0.0"

#endregion


@unique
class ImageType(Enum):
    """
    Enum class containing valid image formats used on safebooru.org.
    """
    PNG = 'p'
    JPG = 'j'
    GIF = 'g'

    @classmethod
    def which(cls, key: str) -> str:
        """
        Returns the file extension of image file; accepts 'p', 'j' or 'g' as
        params, e.g. `ImageType.which('g')` should return ".gif".
        """
        return f".{cls(key).name.lower()}"


class RequestHandler:
    """
    A class containing helper methods for building the initial request to
    safebooru.org and getting response data back.
    """
    @property
    def _user_agent(self) -> str:
        """
        The default user-agent, tried to make it as informative as I could :P.
        """
        sys = f"{uname()[0]} {uname()[4]}; rv:{uname()[2]}"
        return f"SafebooruPy/{__version__} ({sys})"

    @property
    def _headers(self) -> dict:
        """
        The default headers to be used when opening the session.
        """
        return {"User-Agent": self._user_agent}

    @staticmethod
    def url_gen(base_url: str, dest: str, params: dict) -> str:
        """
        Generate valid URL to be used in a request.

        Usage
        -----
        ```
        base = "https://safebooru.org"
        dest = "index.php?"
        params = {"page": "help", "topic": "dapi"}

        # Should output "https://safebooru.org/index.php?page=help&topic=dapi"
        print(RequestHandler.url_gen(base, dest, params))
        ```
        """
        format_params = str()
        for key in params:
            if format_params == str(): format_params += f"{key}={params[key]}"
            else: format_params += f"&{key}={params[key]}"
        return urljoin(base_url, f"{dest}{format_params}")

    @property
    def session(self) -> Session:
        """
        If possible, always only ever use one instance of session; idea being
        it is meant to be persistent, you should only need one.
        """
        session = Session()
        session.headers.update(self._headers)
        return session

    def get(self, url: str, **kwargs) -> "Response Object":
        return self.session.get(url, **kwargs)


@dataclass(frozen=True)
class Image:
    """
    This represents the post image file that is stored on safebooru.org.
    """
    url: str
    ext: str

    @property
    def file_name(self) -> str:
        """
        The default file name to use for image fetch if nothing is entered.
        """
        return f"{urlparse(self.url).query}{ImageType.which(self.ext)}"

    def fetch(self, handler: RequestHandler,
              file_name: str = file_name) -> None:
        """
        Fetches the image file bytes from safebooru.org and writes to a file.

        Usage
        -----
        ```
        handler = RequestHandler()
        img = Image("https://safebooru.org/images/4038/2453" \
                    "29a0ea470d939fdfd436253fbd035a926e0b.jpg?4219608", "j")
        img.fetch(handler)
        ```
        """
        with open(self.file_name, "wb") as file_object:
            file_object.write(handler.get(self.url).content)


@dataclass(frozen=True)
class Posts:
    """
    A dataclass which represents a valid post on safebooru.org.

    limit: How many posts you want to retrieve. There is a hard limit of 100
           posts per request.
    pid:   The page number.
    tags:  The tags to search for. Any tag combination that works on the web
           site will work here. This includes all the meta-tags.
           <https://safebooru.org/index.php?page=tags&s=list>
    cid:   Change ID of the post. This is in Unix time so there are likely
           others with the same value if updated at the same time.
    id:    The post ID.
    """
    limit: int = 100
    pid: int = 0
    tags: str = str()
    cid: int  = 0
    id: int = 0

    @property
    def params(self) -> dict:
        return {
            "page": "dapi",
            "s": "post",
            "q": "index",
            "json": 1,
            "limit": self.limit,
            "pid": self.pid,
            "tags": self.tags,
            "cid": self.cid,
            "id": self.id
        }

    @property
    def url(self) -> str:
        return RequestHandler.url_gen(Safebooru._HOMEPAGE,
                                      Safebooru._DEST, self.params)


@dataclass
class Tags:
    ...
    # TODO: add tags list search option
    # URL Access point: /index.php?page=dapi&s=tag&q=index
    # API Tags doc: <https://gelbooru.com/index.php?page=wiki&s=view&id=18780>


@dataclass(frozen=True)
class Comments:
    """
    A dataclass which represents valid comments on safebooru.org.

    Still decided to have an implementation for comments, however they just
    suck, valid XML data is only returned if the post you are pointing to
    has more than one comment on it, else searching with ID shows nothing.

    post_id:  The ID number of the comment to retrieve.
    show_all: Lists the comments index if set to True and if no ID is used.
    """
    post_id: int = 0
    list_all: bool = False

    @property
    def params(self) -> dict:
        return {
            "page": "dapi",
            "s": "comment",
            "q": "index",
            "post_id": self.post_id if not self.list_all else str()
        }

    @property
    def url(self) -> str:
        return RequestHandler.url_gen(Safebooru._HOMEPAGE,
                                      Safebooru._DEST, self.params)

    def fetch(self, handler: RequestHandler) -> dict:
        """
        Fetch raw text (XML) for specified comment/ all comments and use
        `xmltodict.parse()` to parse the response into a dict.

        Usage
        -----
        ```
        handler = RequestHandler()
        comms = Comments(post_id=4084270)
        print(comms.fetch(handler))
        ```
        """
        return xmltodict.parse(handler.get(self.url).text)

    def fetch_raw(self, handler: RequestHandler) -> str:
        return handler.get(self.url).text


class Safebooru(RequestHandler):
    """
    This is the main class intended for use. It has all of the 'polished'
    methods and properties for scraping useful data from safebooru.org.
    """
    _HOMEPAGE = "https://safebooru.org"
    _DEST = "index.php?"

    def __init__(self, ) -> None:
        super().__init__()
        self.__handler = RequestHandler()


if __name__ == "__main__":
    # TODO: put some program options/ args here instead.

    # print(ImageExt.which('j'))

    handler = RequestHandler()

    post = Posts(id=132)

    print(post.url)
