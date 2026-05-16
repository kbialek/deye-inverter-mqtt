#!/usr/bin/env bash

uv venv -c
uv sync

npm install -g @mariozechner/pi-coding-agent

uv tool install graphifyy
pi install npm:graphify-pi

curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
pi install npm:pi-rtk-optimizer

pi install npm:pi-command-history