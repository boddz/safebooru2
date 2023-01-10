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

Lotta inspiration from: <https://github.com/hentai-chan>

To be released under the GNU GPLv3 licence, which can be found in the source
directory, or with this link: <https://www.gnu.org/licenses/gpl-3.0.en.html>
"""

#region (imports)

from enum import Enum, unique
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from platform import uname
from os import path, makedirs

import requests
import xmltodict
from requests import Session

#endregion

#region (global variables)

__version__ = "v1.0.0"
__license__ = "GNU GPLv3"

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
        From key ('j', 'p' or 'g') return as full version of image ext.
        """
        return f".{cls(key).name.lower()}"


class RequestHandler:
    """
    A class containing helper methods for building the initial requests
    session (using requests.Session) to safebooru.org and getting response
    data back.

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
    def _url_gen(base_url: str, dest: str, params: dict) -> str:
        """
        Generate valid URL to be used in a request.

        Usage
        -----
        ```
        base = "https://safebooru.org"
        dest = "index.php?"
        params = {"page": "help", "topic": "dapi"}

        # Should output "https://safebooru.org/index.php?page=help&topic=dapi"
        print(RequestHandler._url_gen(base, dest, params))
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
    ext: The image file type (jpg: 'j', png: 'p', gif: 'g').
    """
    url: str
    ext: str

    def file_name(self, prefix: str | int = None) -> str:
        """
        The default file name to use for image fetch if nothing is entered.
        """
        prefix = urlparse(self.url).query if prefix is None else prefix
        return f"{prefix}{ImageType.which(self.ext)}"

    def download(self, handler: RequestHandler,
                 filename: str = None, directory: str = None) -> None:
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
        f = self.file_name() if filename is None else self.file_name(filename)
        if directory is not None:
            if path.exists(directory) is False: makedirs(directory)
            f = path.join(directory, f)
        with open(f, "wb") as file_object:
            file_object.write(handler.get(self.url).content)


@dataclass(frozen=True)
class Posts:
    """
    A dataclass which represents a valid post[s] on safebooru.org.

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
    def __params(self) -> dict:
        return {
            "page": "dapi",
            "s": "post",
            "q": "index",
            "json": 1,
            "limit": self.limit,
            "pid": self.pid,
            "tags": self.tags.replace(" ", "+"),
            "cid": self.cid,
            "id": self.id
        }

    @property
    def url(self) -> str:
        """
        Endpoint for accessing data (json) about specified post[s].
        """
        return RequestHandler._url_gen(Safebooru._HOMEPAGE,
                                      Safebooru._DEST, self.__params)

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

    def image_url(self, json: dict) -> dict:
        """
        Using a single post's json, return it's matching image dest.
        """
        url = urljoin(Safebooru._HOMEPAGE, f"images/{json['directory']}/" \
                      f"{json['image']}?{json['id']}")
        return url

    def image_url_index(self, handler: RequestHandler, post_num: int = 0) -> str:
        """
        Get the image dest of specified post_num 0-99 (100).
        """
        json = self.fetch_json(handler)[post_num]  # Json index is post_num.
        url = urljoin(Safebooru._HOMEPAGE, f"images/{json['directory']}/" \
                      f"{json['image']}?{json['id']}")
        return url


@dataclass
class Tags:
    """
    Represents a tag valid tag[s] for a post on safebooru.org.

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
    id: int = None
    limit: int = 100
    after_id: int = None
    name: str = str()
    name_pattern: str = str()

    @property
    def __params(self) -> dict:
        return {
            "page": "dapi",
            "s": "tag",
            "q": "index",
            "id": str() if self.id is None else self.id,  # Dont break params.
            "limit": self.limit,
            "after_id": str() if self.after_id is None else self.after_id,
            "name": self.name,
            "name_pattern": self.name_pattern
        }

    @property
    def url(self) -> str:
        """
        Endpoint for accessing data (XML) about specified tag[s].
        """
        return RequestHandler._url_gen(Safebooru._HOMEPAGE,
                                      Safebooru._DEST, self.__params)

    def fetch_json(self, handler: RequestHandler) -> dict:
        """
        Fetch raw XML for specified tag[s] and use `xmltodict.parse()` to
        parse the response into a dict/ json.

        Usage
        -----
        ```
        handler = RequestHandler(headers=None)
        tags = Tags(limit=4)  # Fetch the first 4 tags on index.
        print(tags.fetch_json(handler))
        ```
        """
        return xmltodict.parse(handler.get(self.url).text)

    def fetch_content(self, handler: RequestHandler) -> str:
        """
        Fetch the raw response content do not parse to dict/ json.
        """
        return handler.get(self.url).text


@dataclass(frozen=True)
class Comments:
    """
    A dataclass which represents valid comments on safebooru.org.

    Still decided to have an implementation for comments, however they just
    suck, valid XML data is only returned if the post you are pointing to
    has more than one comment on it, else searching with ID shows nothing.

    Update: I will not touch comments from now on, after contacting an
    admin on the site and enquiring the above, it is something that sadly
    most likely will not be fixed due to funding/ proprietary software used
    on safebooru.org. It is not a priority.

    post_id:  The ID number of the comment to retrieve.
    show_all: Lists the comments index if set to True and if no ID is used.
    """
    post_id: int = 0
    list_all: bool = False

    @property
    def __params(self) -> dict:
        return {
            "page": "dapi",
            "s": "comment",
            "q": "index",
            "post_id": self.post_id if not self.list_all else str()
        }

    @property
    def url(self) -> str:
        """
        Endpoint for accessing data (XML) about specified comments.
        """
        return RequestHandler._url_gen(Safebooru._HOMEPAGE,
                                      Safebooru._DEST, self.__params)

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
        handler, however property of course cannot be changed by end user.
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

    def image_ext_full(self, json: dict) -> str:
        """
        Using a post's json data, return the full version of image ext.
        """
        return json["image"][-3:]

    def json_from(self, obj: Posts | Comments | Tags) -> dict:
        """
        From a `Posts`, `Tags` or a `Comments` object, return associated json
        or XML data parsed into a dict.

        Usage
        -----
        ```
        sb = Safebooru()
        post = Posts(id=sb.random_id)
        print(sb.json_from(post)[0])
        ```
        """
        return obj.fetch_json(self.handler)

    def content_from(self, obj: Posts | Comments | Tags) -> str:
        """
        From a `Posts`, `Tags` or `Comments` object, return raw content.
        """
        return obj.fetch_content(self.handler)

    def download(self, post_obj: Posts, post_num: int = 0,
                 filename: str = None, directory: str = None) -> None:
        """
        Download the corresponding image for the specified posts obj & index.
        Default index for page is 0 incase ID is used for search (one post).

        Usage
        -----
        ```
        Safebooru().download(Posts(id=4241904), filename="magia")  # With ID.
        Safebooru().download(Posts(tags="akemi_homura"), post_num=4)  # Tags.
        ```
        """
        json = self.json_from(post_obj)[post_num]
        img_url = post_obj.image_url(json)
        Image(img_url, self.image_ext(json)).download(
              self.handler, filename, directory)
