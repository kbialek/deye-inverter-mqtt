#! /bin/bash
bash -c "$(cat config.env | xargs) /usr/bin/python3 deye_docker_entrypoint.py"
