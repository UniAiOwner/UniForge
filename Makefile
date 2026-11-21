.PHONY: install doctor test status

PYTHON ?= /home/uniai/.local/venv314/bin/python
PIP ?= /home/uniai/.local/venv314/bin/pip

install:
	$(PIP) install -e .
	ln -sf /home/uniai/.local/venv314/bin/uniforge /home/uniai/.local/bin/uniforge
	ln -sf /home/uniai/.local/venv314/bin/uniforge /home/uniai/.gemini/antigravity/bin/uniforge

doctor:
	$(PYTHON) -m uniforge.cli doctor

test:
	$(PYTHON) -m uniforge.cli test

status:
	$(PYTHON) -m uniforge.cli status
