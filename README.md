# Safebooru2 (rev2)

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


## Note

This is currently in early development, there will be a lot of changes.

This should in theory work perfectly fine with other similar booru sites that
are using Gelbooru, however my main focus for this project is to target
safebooru.org.


## Setup

(Optional)
I would first recommend setting up a virtual environment:

```bash
cd safebooru2
python3 -m venv venv  # Should work with most systems, might require install.
source venv/bin/activate  # Activate the venv.
```

Install requirements:

```bash
pip install -r requirements.txt
```


## Usage

At the moment, there aren't really any user friendly docs I have created
for this, I have left some basic usage examples in the `main.py` file in the
CWD. You can of course read through the `src/safebooru2/safebooru.py` file
to get a feel for the module as well, I tried documenting everything in it
to the best of my ability.


## Testing

Once setup, you can run all tests directly by doing:

```bash
make test  # Provided GNU make is installed.
```

Or individual tests by doing:

```bash
python3 -m unittest tests/test_foo_bar.py
```
