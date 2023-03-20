# Deye solar inverter MQTT bridge

Reads Deye solar inverter metrics using Modbus over TCP and publishes them over MQTT.

## Supported inverters and metrics
The meaning of certain inverter registers depends on the inverter type.
You should choose metric group(s) that are appropriate to your inverter model.
If your inverter is not listed below, it may still work with one of the already existing metric groups.
Give it a try and experiment. In the worst case it won't work.

When your inverter is not supported, feel free to open an issue in this github project. Maybe, together we will find a way to add the support.

When your inverter turns out to work well with an already exiting metrics group, then please be so kind, and let me know in this [issue](https://github.com/kbialek/deye-inverter-mqtt/issues/41). This will help in building the list of supported inverters below. Thanks!

|Inverter model|Metric groups|
|---|---|
|[Deye SUN-4K-G05](https://www.deyeinverter.com/product/three-phase-string-inverter/sun4-5-6-7-8-10kg03.html)|[string](docs/metric_group_string.md)|
|[Deye SUN1300G3](https://www.deyeinverter.com/product/microinverter-1/sun13002000g3eu230.html)|[micro](docs/metric_group_micro.md)|
|[Deye SUN300G3](https://www.deyeinverter.com/product/microinverter-1/sun300-500g3eu230.html)|[micro](docs/metric_group_micro.md)|
|[Deye SUN600G3](https://www.deyeinverter.com/product/microinverter-1/sun600-800-1000g3eu230-single-phase-4-mppt-microinverter-rapid-shutdown.html)|[micro](docs/metric_group_micro.md)|
|[Bosswerk MI600](https://www.bosswerk.de/wp-content/uploads/2021/12/Datenblatt_Bosswerk_MI6001.pdf)|[micro](docs/metric_group_micro.md)|
|[Deye SUN-5/6/8/10/12K-SG04LP3](https://deye.com/product/sun-5-6-8-10-12k-sg04lp3-5-12kw-three-phase-2-mppt-hybrid-inverter-low-voltage-battery/)|[deye_sg04lp3](docs/metric_group_deye_sg04lp3.md), [deye_sg04lp3_battery](docs/metric_group_deye_sg04lp3_battery.md)|


### Additional MQTT topics
#### **Availability topic**
Reports deye-inverter-mqtt service status (not the inverter/logger status):
* `online` - when the service is connected to the MQTT broker
* `offline` - when the service is disconnected from the MQTT broker

The default topic name is `status` and can be changed in the configuration.

#### **Logger status topic**
Reports solar inverter's logger connectivity status
* `online` - when the service connect to the logger successfully
* `offline` - when the service can't connect to the logger

The default topic name is `logger_status` and can be changed in the configuration.

## Additional features
### Automatically set logger/inverter time
Monitors current logger status and sets the time at the logger/inverter once the connection to it can be established.
This is useful in a setup where the inverter has no access to the public internet, or is cut off from the Solarman cloud services. 
This feature is disabled by default and must be activated by setting `DEYE_FEATURE_SET_TIME` in the config file.

## Installation
1. Copy `config.env.example` as `config.env`
2. Fill in values in `config.env`, see [Configuration](#configuration) for more details
3. Run the container

    ```
    docker run --rm --env-file config.env ghcr.io/kbialek/deye-inverter-mqtt
    ```

### Installation troubleshooting
#### Docker container fails to start with error message: `PermissionError: [Errno 1] Operation not permitted`

It can happen on debian buster based linux distributions, including raspbian.

Solution: Install `libseccomp2` from the backports

```bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 04EE7237B7D453EC 648ACFD622F3D138
echo "deb http://deb.debian.org/debian buster-backports main" | sudo tee -a /etc/apt/sources.list.d/buster-backports.list
sudo apt update
sudo apt install -t buster-backports libseccomp2
```

## Configuration
All configuration options are controlled through environment variables.

* `LOG_LEVEL` - application log level, can be any of `DEBUG`, `INFO`, `WARN`, `ERROR`
* `DEYE_DATA_READ_INTERVAL` - interval between subsequent data reads, in seconds, defaults to 60
* `DEYE_METRIC_GROUPS` - a comma delimited set of:
    * `string` - string inverter
    * `micro` - micro inverter
    * `deye_sg04lp3` - sg04lp3 inverter
    * `deye_sg04lp3_battery` - sg04lp3 battery
* `DEYE_LOGGER_SERIAL_NUMBER` - inverter data logger serial number
* `DEYE_LOGGER_IP_ADDRESS` - inverter data logger IP address
* `DEYE_LOGGER_PORT` - inverter data logger communication port, typically 8899
* `DEYE_FEATURE_MQTT_PUBLISHER` - controls, if the service will publish metrics over mqtt, defaults to `true`
* `DEYE_FEATURE_SET_TIME` - when set to `true`, the service will automatically set the inverter/logger time, defaults to `false`
* `MQTT_HOST` - MQTT Broker IP address
* `MQTT_PORT` - MQTT Broker port, typically 1883
* `MQTT_USERNAME` - MQTT Broker username for authentication 
* `MQTT_PASSWORD` - MQTT Broker password for authentication
* `MQTT_TOPIC_PREFIX` - mqtt topic prefix used for all inverter metrics
* `MQTT_AVAILIBILITY_TOPIC` - mqtt availability topic, defaults to `status`
* `MQTT_LOGGER_STATUS_TOPIC` - logger connectivity status topic, defaults to `logger_status`

## Reading and writing raw register values
The tool allows reading and writing raw register values directly in the terminal.

**USE AT YOUR OWN RISK!** Be sure to know what you are doing. Writing invalid values may damage the inverter.
By using this tool you accept this risk and you take full responsiblity for the consequences.

* To read register value execute:
    ```
    docker run --rm --env-file config.env ghcr.io/kbialek/deye-inverter-mqtt r <reg_address>
    ```
    where `<reg_address>` is register address (decimal)

* To write register value execute:
    ```
    docker run --rm --env-file config.env ghcr.io/kbialek/deye-inverter-mqtt w <reg_address> <reg_value>
    ```
    where `<reg_address>` is register address (decimal), and <reg_value> is a value to set (decimal)

## Development
1. Install python dependencies
    ```
    pip install -r requirements.txt
    ```
1. Running the code
    1. Option 1 - Run the code locally without using Docker
        1. Fill in `config.env` file
        1. Execute `make run`
    1. Option 2 - Build a new docker image locally (for amd64 architecture)
        1. Execute `make docker-build-local`
        1. Fill in `config.env` file    
        1. Execute `make docker-run`
1. To run the tests use:
    1. `make test`
    1. `make test-mqtt` - requires mosquitto MQTT broker binary

    

