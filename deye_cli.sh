#!/bin/bash

set -a; source config.env; set +a
python deye_cli.py "$@"