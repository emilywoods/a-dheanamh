SHELL := /bin/bash
.PHONY: install

install: # sets up venv and installs dependencies
	 python3 -m venv .venv && .venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e .;
