#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
    printf 'Run sh setup.sh first.\n'
    exit 1
fi
exec .venv/bin/python run.py "$@"
