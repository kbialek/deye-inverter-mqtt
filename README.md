# Deye solar inverter MQTT bridge

Reads Deye solar inverter metrics using Modbus over TCP and publishes them over MQTT.

## Supported inverters and metrics
The meaning of certain inverter registers depends on the inverter type.
You should choose metric group(s) that are appropriate to your inverter model.
If your inverter is not listed below, it may still work with one of the already existing metric groups.
Give it a try and experiment. In the worst case it won't work.

When your inverter is not supported, feel free to open an issue in this github project. Maybe, together we will find a way to add the support.

When your inverter turns out to work well with an already exiting metrics group, then please be so kind, and let me know in this [issue](https://github.com/kbialek/deye-inverter-mqtt/issues/41). This will help in building the list of supported inverters below. Thanks!

**The list below is built basing on the reports from the users. Compatiblity is not guaranteed.**

| Inverter model                                                                                                                                                                               | Metric groups                                                                                                                                                                                                              |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Deye SUN-4/5/6/7/8/10/12K-G05-P](https://www.deyeinverter.com/product/three-phase-string-inverter/sun4-5-6-7-8-10-12kg05p-412kw-three-phase-2-mppt.html)                                    | [string](docs/metric_group_string.md), [settings](docs/metric_group_settings.md)                                                                                                                                           |
| [Deye SUN300/500G3-US-220/EU-230](https://www.deyeinverter.com/product/microinverter-1/sun300-500g3eu230.html)                                                                               | [micro](docs/metric_group_micro.md), [settings](docs/metric_group_settings.md)                                                                                                                                             |
| [Deye SUN600/800/1000G3-US-220/EU-230](https://www.deyeinverter.com/product/microinverter-1/sun600-800-1000g3eu230-single-phase-4-mppt-microinverter-rapid-shutdown.html)                    | [micro](docs/metric_group_micro.md), [settings](docs/metric_group_settings.md)                                                                                                                                             |
| [Deye SUN-M60/80/100G3-EU-Q0](https://www.deyeinverter.com/product/microinverter-1/SUN600-800-1000G3US220-EU230-6001000W-Einphasig-2-MPPT-MikroWechselrichter-Schnelles-Herunterfahren.html) | [micro](docs/metric_group_micro.md), [settings](docs/metric_group_settings.md)                                                                                                                                             |
| [Deye SUN1300-2000G3-US-220/EU-230](https://www.deyeinverter.com/product/microinverter-1/sun13002000g3eu230.html)                                                                            | [micro](docs/metric_group_micro.md), [settings](docs/metric_group_settings.md)                                                                                                                                             |
| [Deye SUN-5/6/8/10/12K-SG04LP3](https://deye.com/product/sun-5-6-8-10-12k-sg04lp3-5-12kw-three-phase-2-mppt-hybrid-inverter-low-voltage-battery/)                                            | [deye_sg04lp3](docs/metric_group_deye_sg04lp3.md), [deye_sg04lp3_battery](docs/metric_group_deye_sg04lp3_battery.md), [deye_sg04lp3_ups](docs/metric_group_deye_sg04lp3_ups.md), [settings](docs/metric_group_settings.md) |
| [Deye SUN-5/6K-SG01LP1-US/EU](https://deye.com/product/sun-5-6k-sg01lp1-us-sun-7-6-8k-sg01lp1-us-eu-5-8kw-single-phase-2-mppt-hybrid-inverter-low-voltage-battery/)                          | [deye_hybrid](docs/metric_group_deye_hybrid.md), [deye_hybrid_battery](docs/metric_group_deye_hybrid_battery.md), [settings](docs/metric_group_settings.md)                                                                |
| [Deye SUN-7.6/8K-SG01LP1-US/EU](https://deye.com/product/sun-5-6k-sg01lp1-us-sun-7-6-8k-sg01lp1-us-eu-5-8kw-single-phase-2-mppt-hybrid-inverter-low-voltage-battery/)                        | [deye_hybrid](docs/metric_group_deye_hybrid.md), [deye_hybrid_battery](docs/metric_group_deye_hybrid_battery.md), [settings](docs/metric_group_settings.md)                                                                |
| [Deye SUN-25/30/40/50K-SG01HP3-EU-BM2/3/4](https://deye.com/product/sun-25-30-40-50k-sg01hp3-eu-bm2-3-4-25-50kw-three-phase-2-mppt-hybrid-inverter-low-voltage-battery/) [**(experimental)**](https://github.com/kbialek/deye-inverter-mqtt/issues/110) | [deye_sg01hp3](docs/metric_group_deye_sg01hp3.md), [deye_sg01hp3_battery](docs/metric_group_deye_sg01hp3_battery.md), [deye_sg01hp3_ups](docs/metric_group_deye_sg01hp3_ups.md), [settings](docs/metric_group_settings.md) |

| Meter model                                                         | Metric groups                                     |
| ------------------------------------------------------------------- | ------------------------------------------------- |
| [IGEN DTSD422-D3](https://www.solarmanpv.com/products/smart-meter/) | [igen_dtsd422](docs/metric_group_igen_dtsd422.md) |

Rebranded models
| Inverter model                                                                                                                 | Metric groups                         |
| ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------- |
| [Bosswerk MI600](https://www.bosswerk.de/wp-content/uploads/2021/12/Datenblatt_Bosswerk_MI6001.pdf)                            | [micro](docs/metric_group_micro.md)   |
| [Fuji Solar FU-SUN-4/5/6/7/8/10/12K-G05](https://fuji-solar.com/product/fu-sun-4-5-6-7-8-10-12k-g05-4-12kw-three-phase-2-mppt) | [string](docs/metric_group_string.md) |


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

### Reading inverter settings
The service can optionally read inverter settings. This feature may be useful when you dynamically modify active power regulation factor. Enable it by adding `settings` metric group to `DEYE_METRIC_GROUPS` env variable.

### Writing inverter settings
It is possible to modify selected inverter settings over MQTT. At the moment only active power regulation factor is supported. This feature is disabled by default.

| Setting                 |                             Topic                              | Unit | Value range | Feature flag                           |
| ----------------------- | :------------------------------------------------------------: | ---- | :---------: | -------------------------------------- |
| active power regulation | `{MQTT_TOPIC_PREFIX}/settings/active_power_regulation/command` | %    |    0-120    | `DEYE_FEATURE_ACTIVE_POWER_REGULATION` |

## Additional features
### Automatically set logger/inverter time
Monitors current logger status and sets the time at the logger/inverter once the connection to it can be established.
This is useful in a setup where the inverter has no access to the public internet, or is cut off from the Solarman cloud services. 
This feature is disabled by default and must be activated by setting `DEYE_FEATURE_SET_TIME` in the config file.

### Custom plugins
This feature allows advanced users to extend the functionality of this project. At the moment the plugins can be used to provide custom event processors. This means, that you can now process the readings as you like. No need to rely on MQTT at all anymore.

#### How to implement a plugin
* Plugin is a Python file placed in `plugins` directory. The filename must begin with `deye_plugin_`
* The plugin must define a `DeyePlugin` class. See `plugins/deye_plugin_sample.py` for inspiration.

#### How to start the docker container with custom plugins

  Mount your `plugins` dir into the container filesystem
  ```
  --volume ./plugins:/opt/deye_inverter_mqtt/plugins:ro
  ```

#### List of public plugins
* [stdout-publisher](https://github.com/hoegaarden/deye-inverter-mqtt-plugins/) by @hoegaarden

## Installation
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

## Configuration
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
    * `deye_sg04lp3` - sg04lp3 inverter
    * `deye_sg04lp3_battery` - sg04lp3 battery
    * `deye_sg04lp3_ups` - sg04lp3 ups
    * `deye_sg01hp3` - sg01hp3 inverter
    * `deye_sg01hp3_battery` - sg01hp3 battery
    * `deye_sg01hp3_ups` - sg01hp3 ups
    * `igen_dtsd422`- dtsd422 smart meter
    * `settings` - inverter settings
* `DEYE_LOGGER_SERIAL_NUMBER` - inverter data logger serial number
* `DEYE_LOGGER_IP_ADDRESS` - inverter data logger IP address
* `DEYE_LOGGER_PORT` - inverter data logger communication port, typically 8899
* `DEYE_FEATURE_MQTT_PUBLISHER` - controls, if the service will publish metrics over mqtt, defaults to `true`
* `DEYE_FEATURE_SET_TIME` - when set to `true`, the service will automatically set the inverter/logger time, defaults to `false`
* `DEYE_FEATURE_ACTIVE_POWER_REGULATION` - enables active power regulation control over MQTT command topic
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

### Publish on change feature

The Deye logger usually only updates the measurements only every 5 minutes, so that shorter `DEYE_DATA_READ_INTERVAL` values
would provide duplicate readings of the same measurements. Increasing the read interval to 5 minutes is not a good solution
since it is not known when the measurements are actually updated which could add a delay of one 5 min interval.

To get the latest measurements without much delay but still avoid publishing duplicate readings, the `DEYE_PUBLISH_ON_CHANGE`
option can be enabled. With this feature, a new logger reading is only published if any of the new values differs from the
previous reading.

For the rare case that none of the measurements may have changed between subsequent measurements, a maximum interval between
two published messaged is configured with the variable `DEYE_PUBLISH_ON_CHANGE_MAX_INTERVAL` (default 360 seconds = 6 minutes).

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

## Home Assistant integration

This project currently has no integration with [Home Assistant](https://www.home-assistant.io/). You can manually configure HA to use these data,
or you can write a plugin as described earlier in this document.

For help with integration, see
* [MQTT Client Component](https://esphome.io/components/mqtt.html)
* [MQTT Discovery examples](https://www.home-assistant.io/integrations/mqtt/#discovery-examples)

## Other related projects and resources
* https://github.com/StephanJoubert/home_assistant_solarman
* https://github.com/dasrecht/deye-firmware
* https://github.com/Hypfer/deye-microinverter-cloud-free
* https://github.com/jedie/inverter-connect
* https://github.com/MichaluxPL/Sofar_LSW3

## Development
Read [CONTRIBUTING.md](./CONTRIBUTING.md)
