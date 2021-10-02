.PHONY: install _check_env_file run

VENV_DIR = venv
PIP = $(VENV_DIR)/bin/pip
PYTHON = $(VENV_DIR)/bin/python

install:
	$(PIP) install --requirement requirements.txt --no-input --no-index
	if ! [ -d $(VENV_DIR) ]; \
	then \
	  python -m venv $(VENV_DIR); \
	fi

_check_env_file:
	#! [ -f .env ] && echo Create .env file && exit 1

run: install _check_env_file
	$(PYTHON) src/main.py --database-path backups/backup.$$(date +%F_%H-%M).db \
      --board-id Is2QkLGp \
      --workspace-id gtd37280280 \
      --env-file .env
