#!/usr/bin/env python3

"""
A module containing classes and methods for interacting with the safebooru.org
public API. This is my second API wrapper module for safebooru.org, here's the
link to that: <https://github.com/boddz/safebooru> it is one of my older
projects, some things are poorly done, and I am bored so that's why this
module is a thing.

Lotta inspiration from some great work by: <https://github.com/hentai-chan>

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

    headers: User defined headers to use when sending a request.
    """
    def __init__(self, headers: dict = None) -> None:
        self.headers = headers if headers is not None else self._headers

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
        session.headers.update(
            self.headers if self.headers else self._headers)
        return session

    def get(self, url: str, **kwargs) -> "Response Object":
        return self.session.get(url, **kwargs)


@dataclass(frozen=True)
class Image:
    """
    This represents the post image file that is stored on safebooru.org.

    url: The URL to the images location on safebooru.org.
    ext: The image file type (jpg: j, png: p, gif: g).
    """
    url: str
    ext: str

    @property
    def file_name(self) -> str:
        """
        The default file name to use for image fetch if nothing is entered.
        """
        return f"{urlparse(self.url).query}{ImageType.which(self.ext)}"

    def download(self, handler: RequestHandler,
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

    def fetch_json(self, handler: RequestHandler) -> dict:
        """
        Parse the raw content and convert it into a json style dict.

        Usage
        -----
        ```
        handler = RequestHandler()
        post = Posts(id=Safebooru().random_id)  # Use completely random ID.
        print(post.fetch_json(handler))
        """
        return handler.get(self.url).json()

    def fetch_content(self, handler: RequestHandler) -> str:
        """
        Simply fetch the raw response content do not parse to dict.
        """
        return handler.get(self.url).text

    def image_url(self, handler: RequestHandler, post_num: int = 0) -> str:
        """
        The location where the image for the post is stored on safebooru.org.
        """
        json = self.fetch_json(handler)[post_num]  # Json index is post_num.
        url = urljoin(Safebooru._HOMEPAGE, f"images/{json['directory']}/" \
                      f"{json['image']}?{json['id']}")
        return url


@dataclass
class Tags:
    """
    Represents a tag valid tag for a post on safebooru.org.

    id:           The tag's id in the database. This is useful to grab a
                  specific tag if you already know this value.
    limit:        How many tags you want to retrieve. There is a default limit
                  of 100 per request.
    after_id:     Grab tags whose ID is greater than this value.
    name:         Find tag information based on this value.
    name_pattern: A wildcard search for your query using LIKE. Use _ for
                  single character wildcards or % for multi-character
                  wildcards. (%choolgirl% would act as *choolgirl* wildcard
                  search.)
    """
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

    def fetch_json(self, handler: RequestHandler) -> dict:
        """
        Fetch raw text (XML) for specified comment/ all comments and use
        `xmltodict.parse()` to parse the response into a dict.

        Usage
        -----
        ```
        handler = RequestHandler(headers=None)
        comms = Comments(post_id=4084270)
        print(comms.fetch_json(handler))
        ```
        """
        return xmltodict.parse(handler.get(self.url).text)

    def fetch_content(self, handler: RequestHandler) -> str:
        """
        Fetch the raw response content do not parse to dict.
        """
        return handler.get(self.url).text


class Safebooru(RequestHandler):
    """
    This is the main class intended for use. It has all of the 'polished'
    methods and properties for scraping useful data from safebooru.org.

    id: Specify the post you want to interact with via it's ID.
    """
    _HOMEPAGE = "https://safebooru.org"
    _DEST = "index.php?"

    def __init__(self, headers: dict = None) -> None:
        super().__init__(headers)
        self.__handler = RequestHandler(headers=headers)

    @property
    def handler(self) -> RequestHandler:
        """
        Point to mangled RequestHandler object; easier name for accessing the
        Handler but property of course still cannot be changed by end user.
        """
        return self.__handler

    @property
    def session(self) -> Session:
        """
        Point to self.__handler.session instance object instead.
        """
        return self.__handler.session

    @property
    def _random_redirect_url(self) -> str:
        """
        Get the redirect URL for a random post.
        """
        get_random = "https://safebooru.org/index.php?page=post&s=random"
        return self.handler.get(get_random).url

    @property
    def random_id(self) -> int:
        """
        With `self._random_redirect_url` parse and return the post ID as int.
        """
        return int(urlparse(self._random_redirect_url).query[20:])

    def image_ext(self, json: dict) -> str:
        """
        Using a post's json data, return the shorthand version of image ext.
        """
        return json["image"][-3:-2]

    def json_from(self, obj: Posts | Comments) -> dict:
        """
        From either a post or a comment object, return it's full json.

        Usage
        -----
        ```
        sb = Safebooru()
        post = Posts(id=sb.random_id)
        print(sb.json_from(post)[0])
        ```
        """
        return obj.fetch_json(self.handler)


if __name__ == "__main__":
    """
    This is only for scuffed quick testing purposes, TODO: remove once done.
    """
    #handler = RequestHandler()
    sb = Safebooru()

    post = Posts(id=sb.random_id)
    print(sb.json_from(post)[0])
    #print(post.image_url(handler))
    #print(post.fetch_json(handler))

    #print(sb.random_id)
