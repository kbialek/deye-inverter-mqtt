----
### Do you find this project useful? Buy me a coffee ☕ [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/krbialek)
----

# :sunny: Deye solar inverter MQTT bridge

Reads Deye solar inverter metrics using Modbus over ethernet and publishes them over MQTT.

Supports single inverter installations, as well as fleet of microinverters.

## :bulb: Supported inverters and metrics

The meaning of certain inverter registers depends on the inverter type.
You should choose metric group(s) that are appropriate to your inverter model.
If your inverter is not listed below, it may still work with one of the already existing metric groups.
Give it a try and experiment. In the worst case it won't work.

When your inverter is not supported, feel free to open an issue in this github project. Maybe, together we will find a way to add the support.

When your inverter turns out to work well with an already exiting metrics group, then please be so kind, and let me know in this [issue](https://github.com/kbialek/deye-inverter-mqtt/issues/41). This will help in building the list of supported inverters below. Thanks!

**The list below is built basing on the reports from the users. Compatiblity is not guaranteed.**

| Inverter model                                                                                                                                                                               | Metric groups                                                                                                                                                                                                              |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Deye SUN-4/5/6/7/8/10/12K-G05-P](https://deye.com/product/sun-4-5-6-7-8-10-12k-g05-4-12kw-three-phase-2-mppt/) | [string](docs/metric_group_string.md), [settings](docs/metric_group_settings.md)                                                                                                                                           |
| [Deye SUN300/500G3-US-220/EU-230](https://deye.com/product/sun300-500g3-eu-230-300-500w-single-phase-1-mppt-micro-inverter-rapid-shutdown/) | [micro](docs/metric_group_micro.md), [settings_micro](docs/metric_group_settings_micro.md)                                                                                                                                             |
| [Deye SUN600/800/1000G3-US-220/EU-230](https://deye.com/product/sun600-800-1000g3-eu-230-600-1000w-single-phase-2-mppt-micro-inverter-rapid-shutdown/) | [micro](docs/metric_group_micro.md), [settings_micro](docs/metric_group_settings_micro.md)                                                                                                                                             |
| [Deye SUN-M60/80/100G3-EU-Q0](https://www.deyeinverter.com/product/microinverter-1/SUN600-800-1000G3US220-EU230-6001000W-Einphasig-2-MPPT-MikroWechselrichter-Schnelles-Herunterfahren.html) | [micro](docs/metric_group_micro.md), [settings](docs/metric_group_settings.md)                                                                                                                                             |
| [Deye SUN1300-2000G3-US-220/EU-230](https://deye.com/product/sun1300-2000g3-eu-230-1300-2000w-single-phase-4-mppt-micro-inverter-rapid-shutdown/) | [micro](docs/metric_group_micro.md), [settings](docs/metric_group_settings.md)                                                                                                                                             |
| [Deye SUN-5/6/8/10/12K-SG04LP3](https://deye.com/product/sun-5-6-8-10-12k-sg04lp3-5-12kw-three-phase-2-mppt-hybrid-inverter-low-voltage-battery/)                                            | [deye_sg04lp3](docs/metric_group_deye_sg04lp3.md), [deye_sg04lp3_battery](docs/metric_group_deye_sg04lp3_battery.md), [deye_sg04lp3_ups](docs/metric_group_deye_sg04lp3_ups.md), [deye_sg04lp3_timeofuse](docs/metric_group_deye_sg04lp3_timeofuse.md), [deye_sg04lp3_generator](docs/metric_group_deye_sg04lp3_generator.md), [settings](docs/metric_group_settings.md) |
| [Deye SUN-5/6K-SG01LP1-US/EU](https://deye.com/product/sun-5-6k-sg01lp1-us-sun-7-6-8k-sg01lp1-us-eu-5-8kw-single-phase-2-mppt-hybrid-inverter-low-voltage-battery/)                          | [deye_hybrid](docs/metric_group_deye_hybrid.md), [deye_hybrid_battery](docs/metric_group_deye_hybrid_battery.md), [deye_hybrid_timeofuse](docs/metric_group_deye_hybrid_timeofuse.md), [settings](docs/metric_group_settings.md)                                                                |
| [Deye SUN-7.6/8K-SG01LP1-US/EU](https://deye.com/product/sun-5-6k-sg01lp1-us-sun-7-6-8k-sg01lp1-us-eu-5-8kw-single-phase-2-mppt-hybrid-inverter-low-voltage-battery/)                        | [deye_hybrid](docs/metric_group_deye_hybrid.md), [deye_hybrid_battery](docs/metric_group_deye_hybrid_battery.md), [deye_hybrid_timeofuse](docs/metric_group_deye_hybrid_timeofuse.md), [settings](docs/metric_group_settings.md)                                                                |
| [Deye SUN-12/14/16K-SG01LP1](https://deye.com/product/sun-12-14-16k-sg01lp1-12-16kw-single-phase-2-mppt-hybrid-inverter/)                        | [deye_hybrid](docs/metric_group_deye_hybrid.md), [deye_hybrid_battery](docs/metric_group_deye_hybrid_battery.md), [deye_hybrid_timeofuse](docs/metric_group_deye_hybrid_timeofuse.md), [settings](docs/metric_group_settings.md)                                                                |
| [Deye SUN-6/8/10/12/15/20K-SG01HP3-EU-AM2](https://deye.com/product/sun-6-8-10-12-15-20k-sg01hp3-eu-am2-6-20kw-three-phase-2-mppt-hybrid-inverter-low-voltage-battery/) | [deye_sg01hp3](docs/metric_group_deye_sg01hp3.md), [deye_sg01hp3_battery](docs/metric_group_deye_sg01hp3_battery.md), [deye_sg01hp3_bms](docs/metric_group_deye_sg01hp3_bms.md), [deye_sg01hp3_ups](docs/metric_group_deye_sg01hp3_ups.md), [settings](docs/metric_group_settings.md) |
| [Deye SUN-25/30/40/50K-SG01HP3-EU-BM2/3/4](https://deye.com/product/sun-25-30-40-50k-sg01hp3-eu-bm2-3-4-25-50kw-three-phase-2-mppt-hybrid-inverter-low-voltage-battery/) | [deye_sg01hp3](docs/metric_group_deye_sg01hp3.md), [deye_sg01hp3_battery](docs/metric_group_deye_sg01hp3_battery.md), [deye_sg01hp3_bms](docs/metric_group_deye_sg01hp3_bms.md), [deye_sg01hp3_ups](docs/metric_group_deye_sg01hp3_ups.md), [settings](docs/metric_group_settings.md) |

| Meter model                                                         | Metric groups                                     |
| ------------------------------------------------------------------- | ------------------------------------------------- |
| [IGEN DTSD422-D3](https://www.solarmanpv.com/products/smart-meter/) | [igen_dtsd422](docs/metric_group_igen_dtsd422.md) |

Rebranded models
| Inverter model                                                                                                                 | Metric groups                         |
| ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------- |
| [Bosswerk MI600](https://www.bosswerk.de/wp-content/uploads/2021/12/Datenblatt_Bosswerk_MI6001.pdf)                            | [micro](docs/metric_group_micro.md)   |
| [Fuji Solar FU-SUN-4/5/6/7/8/10/12K-G05](https://fuji-solar.com/product/fu-sun-4-5-6-7-8-10-12k-g05-4-12kw-three-phase-2-mppt) | [string](docs/metric_group_string.md) |


## :hammer_and_wrench: Installation
The communication with the logger can be performed using either Modbus/TCP or Modbus/AT protocol.
This project has been started with Modbus/TCP protocol support and it's still the default one.
However, logger firmware versions 2.x does not seem to expose Modbus/TCP interface anymore, hence Modbus/AT protocol support has been implemented. Use `DEYE_LOGGER_PROTOCOL` environment variable to select
the communication protocol.
Please note, that Modbus/TCP uses tcp/ip, while Modbus/AT uses udp/ip communication. 

1. Copy `config.env.example` as `config.env`
2. Fill in values in `config.env`, see [Configuration](#configuration) for more details

### Option 1: Using Docker directly
1. Run the container

    ```
    docker run -d --name deye-mqtt \
        --env-file config.env \
        --restart unless-stopped \
        ghcr.io/kbialek/deye-inverter-mqtt
    ```
    * `-d` will detach the container, so it will run in the background
    * `--restart=unless-stopped` will make docker to restart the container on host reboot
2. Stop and remove the container
    ```
    docker stop deye-mqtt
    docker rm -v deye-mqtt
    ```
3. Inspect the logs
    ```
    docker logs deye-mqtt
    ```

### Option 2: Using Docker Compose
1. Create or modify your own `docker-compose.yaml` file. Here is [a working example](docker-compose.yaml)
2. Run the container

    ```
    docker compose -f <path-to-docker-compose.yaml> up -d
    ```
    * replace `<path-to-docker-compose.yaml>` with path to your `docker-compose.yaml` 
3. Stop and remove the container
    ```
    docker compose -f <path-to-docker-compose.yaml> down -v
    ```

### Connecting to MQTT Broker over TLS
1. Put certificates and client private key in a folder of your choice. The following files are required.
   1. `ca.crt`
   2. `client.crt`
   3. `client.key`
   
   Check configuration section if you want to use alternative file names.
2. Mount certificates folder in a docker container by adding `--volume` option to the command as follows:
   ```
   --volume <certs_folder>:/opt/deye_inverter_mqtt/certs:ro
   ```
    * replace `<certs_folder>` with the certificates folder location of your choice
3. Enable TLS in the configuration.
    ```
    MQTT_TLS_ENABLED=true
    ```
4. Start the container

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

#### Network connectivity issues

These problems typically manifest with timeout errors. 

The first thing to check is, if given network address is reachable from within the docker container.
In order to do this run the following commands:
1. Login to your docker host
2. Start the container in shell mode: `docker run --rm -ti --entrypoint /bin/sh ghcr.io/kbialek/deye-inverter-mqtt`
3. Install `telnet` by running `apk update && apk add busybox-extras`
4. Check connectivity: `telnet <ip> <port>`
   1. Substitute `<ip>` and `<port>` with appropriate values
5. You should see either:
   1. `Connected to <ip>` - connection works fine. The next step is to enable DEBUG logs in `config.env` and open a github issue
   2. `telnet: can't connect to remote host (<ip>): Connection refused` - The next step is: fix your network configuration

#### Random read timeouts 

For best performance, multiple Modbus registers are read at once, in so called register ranges. It's been reported [here](https://github.com/kbialek/deye-inverter-mqtt/issues/141) that Deye-SUN-5K-SG03LP1 reading times out when more than 16 registers is requested at once. To mitigate this problem you may try to set `DEYE_LOGGER_MAX_REG_RANGE_LENGTH` to lower number.


## :gear: Configuration
All configuration options are controlled through environment variables.

* `LOG_LEVEL` - application log level, can be any of `DEBUG`, `INFO`, `WARN`, `ERROR`, defaults to `INFO`
* `LOG_STREAM` - log destination stream, can be any of `STDOUT`, `STDERR`, defaults to `STDOUT`
* `DEYE_PUBLISH_ON_CHANGE` - when set to `true`, the event data will only be published if it has changed compared to last readings, defaults to `false`
* `DEYE_PUBLISH_ON_CHANGE_MAX_INTERVAL` - when `DEYE_PUBLISH_ON_CHANGE` is `true`, this variable defines the maximum age of a valid event list in seconds, defaults to 360 seconds
* `DEYE_DATA_READ_INTERVAL` - interval between subsequent data reads, in seconds, defaults to 60
* `DEYE_METRIC_GROUPS` - a comma delimited set of:
    * `string` - string inverter
    * `micro` - micro inverter
    * `deye_hybrid` - hybrid inverter
    * `deye_hybrid_battery` - hybrid inverter battery
    * `deye_hybrid_timeofuse` - hybrid inverter time-of-use settings
    * `deye_sg04lp3` - sg04lp3 inverter
    * `deye_sg04lp3_battery` - sg04lp3 battery
    * `deye_sg04lp3_ups` - sg04lp3 ups
    * `deye_sg04lp3_timeofuse` - sg04lp3 time-of-use settings
    * `deye_sg01hp3` - sg01hp3 inverter
    * `deye_sg01hp3_battery` - sg01hp3 battery
    * `deye_sg01hp3_bms` - sg01hp3 bms
    * `deye_sg01hp3_ups` - sg01hp3 ups
    * `igen_dtsd422`- dtsd422 smart meter
    * `settings` - inverter settings, all types except micro
    * `settings_micro` - inverter settings for micro inverters
* `DEYE_LOGGER_COUNT` - declares the number of inverters, and therefore loggers to connect, optional, defaults to `0`, which means, that multi-inverter support is disabled
* `DEYE_LOGGER_SERIAL_NUMBER` or `DEYE_LOGGER_{N}_SERIAL_NUMBER` - inverter data logger serial number
* `DEYE_LOGGER_IP_ADDRESS` or `DEYE_LOGGER_{N}_IP_ADDRESS` - inverter data logger IP address
* `DEYE_LOGGER_PORT` or `DEYE_LOGGER_{N}_PORT` - inverter data logger communication port, optional, defaults to 8899 for Modbus/TCP, and 48899 for Modbus/AT
* `DEYE_LOGGER_PROTOCOL` or `DEYE_LOGGER_{N}_PROTOCOL` - inverter communication protocol, optional, either `tcp` for Modbus/TCP, or `at` for Modbus/AT, defaults to `tcp`
* `DEYE_LOGGER_MAX_REG_RANGE_LENGTH` or `DEYE_LOGGER_{N}_MAX_REG_RANGE_LENGTH`- controls maximum number of registers to be read in a single Modbus registers read operation, defaults to 256
* `DEYE_FEATURE_MQTT_PUBLISHER` - controls, if the service will publish metrics over mqtt, defaults to `true`
* `DEYE_FEATURE_SET_TIME` - when set to `true`, the service will automatically set the inverter/logger time, defaults to `false`
* `DEYE_FEATURE_ACTIVE_POWER_REGULATION` - enables active power regulation control over MQTT command topic
* `DEYE_FEATURE_TIME_OF_USE` - enables Time Of Use feature control over MQTT
* `DEYE_FEATURE_MULTI_INVERTER_DATA_AGGREGATOR` - enables multi-inverter data aggregation and publishing
* `MQTT_HOST` - MQTT Broker IP address
* `MQTT_PORT` - MQTT Broker port, , defaults to `1883`
* `MQTT_USERNAME` - MQTT Broker username for authentication, defaults to `None`
* `MQTT_PASSWORD` - MQTT Broker password for authentication, defaults to `None`
* `MQTT_TOPIC_PREFIX` - mqtt topic prefix used for all inverter metrics, defaults to `deye`
* `MQTT_AVAILABILITY_TOPIC` - mqtt availability topic, defaults to `status`
* `MQTT_LOGGER_STATUS_TOPIC` - logger connectivity status topic, defaults to `logger_status`
* `MQTT_TLS_ENABLED` - enables TLS encryption for the communication with the broker, defaults to `false`
* `MQTT_TLS_INSECURE` - Set to true in order to skip server certificate verification, defaults to `false`
* `MQTT_TLS_CA_CERT_PATH` - CA certificate location to be used instead of the system certification authority, defaults to `None`
* `MQTT_TLS_CLIENT_CERT_PATH` - Client certificate location for TLS based authentication, defaults to `None`
* `MQTT_TLS_CLIENT_KEY_PATH` - Client private key location for TLS based authentication, defaults to `None`
* `PLUGINS_DIR` - Path to a directory containing custom plugins extending the functionality of the service
* `PLUGINS_ENABLED` - A list of plugin names that will be loaded when successfully discovered in `PLUGINS_DIR`, defaults to `[]`

## ➕ Additional features
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

### Monitoring a fleet of microinverters
This feature enables monitoring of *N* microinverters from a single service instance (docker container), which simplifies the installation and configuration.
It is designed to monitor a fleet of microinverters.
To activate this feature, set `DEYE_LOGGER_COUNT` environment variable to the number of loggers you would like to connect to. Next configure each logger by adding a set of environment variables, as follows:
```
DEYE_LOGGER_{N}_IP_ADDRESS=192.168.XXX.YYY
DEYE_LOGGER_{N}_SERIAL_NUMBER=0123456789
# Optionals
DEYE_LOGGER_{N}_PROTOCOL=at
DEYE_LOGGER_{N}_PORT=48899
DEYE_LOGGER_{N}_MAX_REG_RANGE_LENGTH_PORT=256
```
Replace `{N}` with logger index. All loggers in the range of 1 to `DEYE_LOGGER_COUNT` must be configured.

All other configuration options, in particular the metric groups, are shared by all configured loggers. For example, if you set `DEYE_FEATURE_SET_TIME=true`, it will activate set-time feature for all configured loggers.

Each logger gets its own MQTT topic prefix `{MQTT_TOPIC_PREFIX}/{N}`

Additionally, you can enable multi-inverter data aggregation. Set `DEYE_FEATURE_MULTI_INVERTER_DATA_AGGREGATOR=true` to compute and report `Aggregated daily energy` and `Aggregated AC active power` for the entire fleet. See [aggregated metrics](docs/metric_group_aggregated.md)

### Automatically set logger/inverter time
Monitors current logger status and sets the time at the logger/inverter once the connection to it can be established.
This is useful in a setup where the inverter has no access to the public internet, or is cut off from the Solarman cloud services. 
This feature is disabled by default and must be activated by setting `DEYE_FEATURE_SET_TIME` in the config file.

### Reading inverter settings
The service can optionally read inverter settings. This feature may be useful when you dynamically modify active power regulation factor. Enable it by adding `settings` or `settings_micro` metric group to `DEYE_METRIC_GROUPS` env variable.

### Writing inverter settings
It is possible to modify selected inverter settings over MQTT.

| Setting                 |                             Topic                              | Unit | Value range | Feature flag                           |
| ----------------------- | :------------------------------------------------------------: | ---- | :---------: | -------------------------------------- |
| active power regulation | `{MQTT_TOPIC_PREFIX}/settings/active_power_regulation/command` | %    |    0-120    | `DEYE_FEATURE_ACTIVE_POWER_REGULATION` |
| time of use | `{MQTT_TOPIC_PREFIX}/timeofuse/time/(1-6)/command` | time | 0000 - 2359 | `DEYE_FEATURE_TIME_OF_USE` |
| time of use | `{MQTT_TOPIC_PREFIX}/timeofuse/power/(1-6)/command` | W | 0 - max power<sup>(1)</sup> | `DEYE_FEATURE_TIME_OF_USE` |
| time of use | `{MQTT_TOPIC_PREFIX}/timeofuse/voltage/(1-6)/command` | V | 0.00 - 63.00 | `DEYE_FEATURE_TIME_OF_USE` |
| time of use | `{MQTT_TOPIC_PREFIX}/timeofuse/soc/(1-6)/command` | % | 0 - 100 | `DEYE_FEATURE_TIME_OF_USE` |
| time of use | `{MQTT_TOPIC_PREFIX}/timeofuse/enabled/(1-6)/command` | On/Off | 0,1 | `DEYE_FEATURE_TIME_OF_USE` |
| time of use | `{MQTT_TOPIC_PREFIX}/timeofuse/control/command` | string | write, reset | `DEYE_FEATURE_TIME_OF_USE` |

<sup>(1)</sup> max inverter power in Watts e.g. 8000, 10000 or 12000

#### Writing Time Of Use configuration

Prerequisites:
1. Set `DEYE_FEATURE_TIME_OF_USE` to `true`
2. Enable time-of-use metric group that's appropriate to your inverter model, e.g. `deye_sg04lp3_timeofuse`

Time Of Use configuration is modified using the following workflow:

1. The service reads Time Of Use configuration from the inverter and keeps it in the memory. This step happens automatically at each data read from the inverter.
2. You send modifications over `{MQTT_TOPIC_PREFIX}/timeofuse/*/*/command` topics as needed. See the table above for more details about used MQTT topics. These changes are not immediately written to the inverter. They are **buffered** in the service memory instead.
3. Send `write` command to topic `{MQTT_TOPIC_PREFIX}/timeofuse/control/command`. It will build a new Time Of Use configuration by putting your changes on top of the inverter configuration present in the service memory. Next the entire Time Of Use configuration is sent to the inverter. The modifications are cleared, and you can start over sending new modifications.
4. Alternatively send `reset` command to purge buffered modifications without writing them to the inverter.

### Publish on change feature

The Deye logger usually only updates the measurements only every 5 minutes, so that shorter `DEYE_DATA_READ_INTERVAL` values
would provide duplicate readings of the same measurements. Increasing the read interval to 5 minutes is not a good solution
since it is not known when the measurements are actually updated which could add a delay of one 5 min interval.

To get the latest measurements without much delay but still avoid publishing duplicate readings, the `DEYE_PUBLISH_ON_CHANGE`
option can be enabled. With this feature, a new logger reading is only published if any of the new values differs from the
previous reading.

For the rare case that none of the measurements may have changed between subsequent measurements, a maximum interval between
two published messaged is configured with the variable `DEYE_PUBLISH_ON_CHANGE_MAX_INTERVAL` (default 360 seconds = 6 minutes).

### Home Assistant integration

This project currently has no built-in integration with [Home Assistant](https://www.home-assistant.io/). You can use the
[Deye MQTT HA Plugin](https://sr.ht/~carstengrohmann/deye-mqtt-ha-plugin/) to integrate all data published via
MQTT into [Home Assistant](https://www.home-assistant.io/).

## 🔌 Custom plugins
This feature allows advanced users to extend the functionality of this project. At the moment the plugins can be used to provide custom event processors. This means, that you can now process the readings as you like. No need to rely on MQTT at all anymore.

### How to implement a plugin
* Plugin is a Python file placed in `plugins` directory. The filename must begin with `deye_plugin_`
* The plugin must define a `DeyePlugin` class. See `plugins/deye_plugin_sample.py` for inspiration.

### How to start the docker container with custom plugins

  Mount your `plugins` dir into the container filesystem
  ```
  --volume ./plugins:/opt/deye_inverter_mqtt/plugins:ro
  ```

### List of public plugins
* [stdout-publisher](https://github.com/hoegaarden/deye-inverter-mqtt-plugins/) by @hoegaarden
* [Deye MQTT HA Plugin](https://sr.ht/~carstengrohmann/deye-mqtt-ha-plugin/) (mirrored on [GitHub](https://github.com/CarstenGrohmann/deye-mqtt-ha-plugin)) by Carsten Grohmann

## Reading and writing raw register values
The tool allows reading and writing raw register values directly in the terminal.

**USE AT YOUR OWN RISK!** Be sure to know what you are doing. Writing invalid values may damage the inverter.
By using this tool you accept this risk, and you take full responsibility for the consequences.

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

## 👀 Other related projects and resources
* https://github.com/StephanJoubert/home_assistant_solarman
* https://github.com/dasrecht/deye-firmware
* https://github.com/Hypfer/deye-microinverter-cloud-free
* https://github.com/jedie/inverter-connect
* https://github.com/MichaluxPL/Sofar_LSW3
* https://github.com/s10l/deye-logger-at-cmd

## Development
Read [CONTRIBUTING.md](./CONTRIBUTING.md)
