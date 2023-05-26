#!/bin/bash
#
# This script will install a systemd service to run 
# deye-inverter-mqtt
#
# It assumes to be stored in the systemd subdirectory of your
# deye-inverter-mqtt tree.


SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
DEYE_DIR="${SCRIPT_DIR%/systemd}"

if [[ ! -d "${DEYE_DIR}" ]] || [[ ! -r "${DEYE_DIR}/requirements.txt" ]]
then
	echo "deye-inverter-mqtt not found."
	exit 1
fi

if ! [[ -r "${DEYE_DIR}/config.env" ]]
then
	echo "You first need to create ${DEYE_DIR}/config.env."
	exit 1
fi

user=""
while [[ -z "$user" ]]
do
	echo "Give the name of the user that shall run the MQTT bridge."
	echo -n "> "
	read -r user
done

if ! id "$user" >/dev/null
then
	echo "User '$user' does not exist, please create it first."
	echo "Usually you can use 'useradd -r $user' to achieve that."
	echo "If in doubt, please read the manual for your operation system."
	exit 0
fi

echo "Creating python virtual environment ..."
python -m venv "${DEYE_DIR}/venv" || { echo "Failed!"; exit 1; }

echo "Activating the virtual environment ..."
source "${DEYE_DIR}/venv/bin/activate"

echo "Installing python dependencies ..."
pip install -r "${DEYE_DIR}/requirements.txt" || { echo "Failed!"; exit 1; }

echo "Leaving the virtual environment ..."
deactivate

echo "Generating systemd service file ..."
cp "${SCRIPT_DIR}/deye-inverter-mqtt.service.template" \
	"${SCRIPT_DIR}/deye-inverter-mqtt.service"
sed -i -e "s#/path/to/deye-inverter-mqtt/#${DEYE_DIR}#" \
	-e "s#deyeuser#$user#" "${SCRIPT_DIR}/deye-inverter-mqtt.service"

while [[ ! "$usesudo" =~ y|n ]]
do
	echo "Using sudo to install service? [y|n]"
	echo -n "> "
	read -r usesudo
done

if [[ "$usesudo" == "y" ]]
then
	echo "Checking sudo command ..."
	if [[ $(sudo id -u) != 0 ]]
	then
		echo "Unable to gain root access."
		usesudo=n
	fi
fi

if [[ "$usesudo" == "n" ]]
then
	cat <<EOF
You need to run the following commands as root:
1.> cp \"${SCRIPT_DIR}/deye-inverter-mqtt.service\" /etc/systemd/system/
2.> systemctl deamon-reload
3.> systemctl start deye-inverter-mqtt.service
EOF
	exit 0
fi

echo "Copying service file ..."
sudo cp "${SCRIPT_DIR}/deye-inverter-mqtt.service" /etc/systemd/system/

echo "Reloading service configurations ..."
sudo systemctl deamon-reload

echo "Starting service ..."
sudo systemctl start deye-inverter-mqtt.service

:
