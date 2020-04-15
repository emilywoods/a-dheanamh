SHELL := /bin/bash
.PHONY: install

.PHONY: install
install:  ## sets up venv and installs the python app to it
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt


.PHONY: format
format: install
	.venv/bin/black .

.PHONY: run
run: install ## start app
	.venv/bin/python weekly.py -c ../cron.config

.PHONY: clean
clean: ## clean up afterwards
	rm -rf .venv

