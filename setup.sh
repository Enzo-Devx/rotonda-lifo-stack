#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else "Python 3.10 or newer is required.")'
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
printf '\nSetup complete. Run: sh start.sh\n'
