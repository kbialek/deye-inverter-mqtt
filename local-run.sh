#!/usr/bin/env bash
# Runs the application locally.
# Supports two execution modes:
# 1. When docker is installed and Python's virtual env is configured, then runs the appliction within a temporary docker container.
#    The advantage is that config.env file is read in the same way as it will be read by docker in "production".
# 2. Otherwise fallsback to running the application in bash

set -f -o pipefail

readonly DOCKER_IMAGE="$1"

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "[ERROR] Python virtual env is not activated. Run "poetry shell" first."
    exit 1
fi

if (which docker > /dev/null) && [[ -n "$DOCKER_IMAGE" ]]; then
    echo "[local-run] Using docker" 1>&2
    readonly python_version=$(find "$VIRTUAL_ENV" -name site-packages | grep -o "python[^/]*")
    docker run \
        --rm \
        --env-file config.env \
        -e PYTHONPATH="/opt/venv/lib/$python_version/site-packages" \
        -v "$VIRTUAL_ENV":/opt/venv:ro \
        -v "$PWD"/src:/opt/src:ro \
        -v "$PWD"/plugins:/opt/plugins:ro \
        -w "/opt" \
        "$DOCKER_IMAGE" \
        python src/deye_docker_entrypoint.py
else
    echo "[local-run] Using bash" 1>&2
    bash -c "set -a; source config.env; python src/deye_docker_entrypoint.py"
fi