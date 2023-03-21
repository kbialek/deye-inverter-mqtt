# Systemd service file

1. Create or define a user that should run the service
   Every step is done as that user if not stated differently.
1. Create a python venv
   ```
   python -m venv /path/to/deye-inverter-mqtt/venv
   ```
1. Activate the venv
   ```
   source /path/to/deye-inverter-mqtt/venv/bin/activate
   ```
1. Install python dependencies
    ```
    pip install -r /path/to/deye-inverter-mqtt/requirements.txt
    ```
1. Leave the venv
    ```
    deactivate
    ```
1. Create `/path/to/deye-inverter-mqtt/config.env` (see https://github.com/kbialek/deye-inverter-mqtt#configuration)
1. Adjust the user and path in `deye-inverter-mqtt.service`
   - `deyeuser` => your choise from above
   -  `/path/to/deye-inverter-mqtt/` => your installation path
1. As root: Put `deye-inverter-mqtt.service` to `/etc/systemd/system/`
1. As root: Check the service
   ```
   systemctl deamon-reload
   systemctl start deye-inverter-mqtt.service
   systemctl status deye-inverter-mqtt.service
   ```
1. As root: If everything is fine, enable the service
   ```
   systemctl enable deye-inverter-mqtt.service
   ```
