PY := python3
PY_SITE_PACKAGES := venv/lib64/python3.10/site-packages/
CLEAN := src/safebooru2/__pycache__ tests/__pycache__
TEST := tests/test_request_handler.py tests/test_image_type.py \
		tests/test_image.py tests/test_posts.py tests/test_comments.py \

all: main

main:
	$(PY) main.py

.PHONY: test install uninstall clean

test:
	$(PY) -m unittest $(TEST)

install: clean  # This should be illegal... it works though...
	cp -r src/safebooru2 $(PY_SITE_PACKAGES)

uninstall:
	rm -rf $(PY_SITE_PACKAGES)/safebooru2

clean:
	rm -rf $(CLEAN)
