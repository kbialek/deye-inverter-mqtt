# build in docker:
sudo docker compose up --build -d

# DEBUGGING
# 1. debugging ist direkt in VSC implementiert: benutze "Python: Debug with config.env"

# # 2. python im terminal:
# # uv venv --python 3.12.8
# # uv pip install -r requirements.txt
# source .venv/bin/activate
# set -a
# source config.env
# python3 ./src/deye_docker_entrypoint.py r 672

# kbialek's direct run:
./local-run.sh

# aus portainer sh console heraus:
python3 ./deye_docker_entrypoint.py r 672




# GIT - forks   
# git remote -v
origin      git@github.com:aperiodicchain/deye-inverter-mqtt.git (fetch/push)
upstream    git@github.com:kbialek/deye-inverter-mqtt.git (fetch/push)

# show all branches (local and remote)
git branch --all