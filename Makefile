PY := python
PY_SITE_PACKAGES := venv/lib64/python3.10/site-packages/
CLEAN := src/safebooru2/__pycache__ tests/__pycache__

all: main

main:
	$(PY) main.py

.PHONY: test install uninstall clean

test:
	$(PY) -m unittest tests/test*

install: clean  # This should be illegal... it works though...
	cp -r src/safebooru2 $(PY_SITE_PACKAGES)

uninstall:
	rm -rf $(PY_SITE_PACKAGES)/safebooru2

clean:
	rm -rf $(CLEAN)
