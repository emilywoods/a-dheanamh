SHELL := /bin/bash

.PHONY: venv
venv:
	python3 -m venv .venv


.PHONY: install
install: venv ## sets up venv and installs the aw-yay CLI app to it
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e .


.PHONY: format
format: install
	.venv/bin/black .

.PHONY: clean
clean: ## clean up afterwards
	rm -rf .venv

