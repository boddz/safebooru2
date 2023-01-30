"""
PIP/ PyPI packaging setup.

Ref: https://setuptools.pypa.io/en/latest/userguide/quickstart.html
"""

import re
from setuptools import setup, find_packages
from pathlib import Path


# https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

with open("./src/safebooru2/safebooru.py", "r") as file_object:
    content = file_object.read()
    package_version = re.search(r'__version__ = "(.*?)"', content).group(1)

setup(
    name="safebooru2",
    author="boddz",
    author_email="boddz.dev@gmail.com",
    license="The GNU General Public License v3.0",
    description="Synchronous API wrapper module for safebooru.org" \
                "implemented in Python3. ",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=package_version,
    project_urls={"GitHub": "https://github.com/boddz/safebooru2"},
    install_requires=[
        "certifi==2022.12.7",
        "charset-normalizer==2.1.1",
        "idna==3.4",
        "requests==2.28.1",
        "urllib3==1.26.13",
        "xmltodict==0.13.0"
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)

print("\nSetup finished, wheel file made. Install: pip install dist/*.whl")
