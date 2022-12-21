PY := python3
CLEAN := src/safebooru/__pycache__ tests/__pycache__
TEST := tests/test_request_handler.py tests/test_image_type.py \
		tests/test_image.py tests/test_posts.py

all: main

main:
	$(PY) main.py

.PHONY: test clean

test:
	$(PY) -m unittest $(TEST)

clean:
	rm -rf $(CLEAN)
