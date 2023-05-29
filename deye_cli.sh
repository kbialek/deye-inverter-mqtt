#!/bin/bash

set -a; source config.env; set +a
python src/deye_cli.py "$@"