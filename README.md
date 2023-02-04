# Deye solar inverter MQTT bridge

Reads Deye solar inverter metrics using Modbus over TCP and publishes them over MQTT.

Tested with:
* [Deye SUN-4K-G05](https://www.deyeinverter.com/product/three-phase-string-inverter/sun4-5-6-7-8-10kg03.html) and Logger S/N 23xxxxxxxx
* [Deye SUN1300G3](https://www.deyeinverter.com/product/microinverter-1/sun13002000g3eu230.html) and Logger S/N 41xxxxxxxx
* [Deye SUN600G3](https://www.deyeinverter.com/product/microinverter-1/sun600-800-1000g3eu230-single-phase-4-mppt-microinverter-rapid-shutdown.html) and Device S/N 41xxxxxxxx
* Bosswerk mi600 (Rebrand of Deye SUN600G3) and Logger S/N 410xxxxxxx
* Bosswerk mi300.1 (Rebrand of Deye) and Logger S/N 415xxxxxxx

To make Bosswerk mi600 and mi300 ready to be read, additional hints at the end of this page

## Supported metrics
The meaning of certain registers depends on the inverter type. 
For example, **string** inverters use registers 0x46 - 0x4e to report AC phase voltage/current.
On the other hand, **micro** inverters use this same registers to report pv1-pv4 cumulative energy.
Generally there are three types of inverters documented in the specification: **string**, **micro** and **hybrid**.
In the table below you can see, that the metrics are assigned to specific groups.
Empty value indicates a general purpose metric, that is available in all type of inverters.
You should specify the set of groups that is appropriate for your inverter in `DEYE_METRIC_GROUPS` environment variable,
otherwise only general purpose metrics will be reported over mqtt. Typically you should set it to either **string** or **micro**. 
Additional groups may be added in the future.

|Metric|Modbus address|MQTT topic suffix|Unit|Groups|
|---|:-:|---|:-:|---|
|Production today|0x3c|`day_energy`|kWh||
|Uptime|0x3e|`uptime`|minutes||
|Total Production (Active)|0x3F - 0x40|`total_energy`|kWh||
|Daily Production 1|0x41|`dc/pv1/day_energy`|kWh|micro|
|Daily Production 2|0x42|`dc/pv2/day_energy`|kWh|micro|
|Daily Production 3|0x43|`dc/pv3/day_energy`|kWh|micro|
|Daily Production 4|0x44|`dc/pv4/day_energy`|kWh|micro|
|Total Production 1|0x45 - 0x46|`dc/pv1/total_energy`|kWh|micro|
|Total Production 2|0x47 - 0x48|`dc/pv2/total_energy`|kWh|micro|
|Total Production 3|0x4a - 0x4b|`dc/pv3/total_energy`|kWh|micro|
|Total Production 4|0x4d - 0x4e|`dc/pv4/total_energy`|kWh|micro|
|AC Phase 1 voltage|0x49|`ac/l1/voltage`|V|string, micro|
|AC Phase 2 voltage|0x4a|`ac/l2/voltage`|V|string|
|AC Phase 3 voltage|0x4b|`ac/l3/voltage`|V|string|
|AC Phase 1 current|0x4c|`ac/l1/current`|A|string, micro|
|AC Phase 2 current|0x4d|`ac/l2/current`|A|string|
|AC Phase 3 current|0x4e|`ac/l3/current`|A|string|
|AC Phase 1 power|computed|`ac/l1/power`|W|string, micro|
|AC Phase 2 power|computed|`ac/l2/power`|W|string|
|AC Phase 3 power|computed|`ac/l3/power`|W|string|
|AC Frequency|0x4f|`ac/freq`|Hz||
|Operating power|0x50|`operating_power`|W|string, micro|
|DC total power|0x52|`dc/total_power`|W|string|
|DC total power|computed|`dc/total_power`|W|micro|
|AC apparent power|0x54|`ac/apparent_power`|W|string|
|AC active power|0x56 - 0x57|`ac/active_power`|W|string, micro|
|AC reactive power|0x58|`ac/reactive_power`|W|string|
|Radiator temperature|0x5a|`radiator_temp`|C|string, micro|
|IGBT temperature|0x5b|`igbt_temp`|C|string|
|DC PV1 voltage|0x6d|`dc/pv1/voltage`|V||
|DC PV1 current|0x6e|`dc/pv1/current`|A||
|DC PV1 power|computed|`dc/pv1/power`|W||
|DC PV2 voltage|0x6f|`dc/pv2/voltage`|V||
|DC PV2 current|0x70|`dc/pv2/current`|A||
|DC PV2 power|computed|`dc/pv2/power`|W||
|DC PV3 voltage|0x71|`dc/pv3/voltage`|V||
|DC PV3 current|0x72|`dc/pv3/current`|A||
|DC PV3 power|computed|`dc/pv3/power`|W||
|DC PV4 voltage|0x73|`dc/pv4/voltage`|V||
|DC PV4 current|0x74|`dc/pv4/current`|A||
|DC PV4 power|computed|`dc/pv4/power`|W||

## Installation
1. Copy `config.env.example` as `config.env`
2. Fill in values in `config.env`
3. Run the container

    ```
    docker run --rm --env-file config.env ghcr.io/kbialek/deye-inverter-mqtt
    ```


## Configuration
All configuration options are controlled through environment variables.

* `LOG_LEVEL` - application log level, can be any of `DEBUG`, `INFO`, `WARN`, `ERROR`
* `DEYE_DATA_READ_INTERVAL` - interval between subsequent data reads, in seconds, defaults to 60
* `DEYE_METRIC_GROUPS` - a comma delimited set of:
    * `string` - set when connecting to a string inverter
    * `micro` - set when connecting to a micro inverter
* `DEYE_LOGGER_SERIAL_NUMBER` - inverter data logger serial number
* `DEYE_LOGGER_IP_ADDRESS` - inverter data logger IP address
* `DEYE_LOGGER_PORT` - inverter data logger communication port, typically 8899
* `MQTT_HOST`
* `MQTT_PORT`
* `MQTT_USERNAME`
* `MQTT_PASSWORD`
* `MQTT_TOPIC_PREFIX` - mqtt topic prefix used for all inverter metrics

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

## Hints for Bosswerk mi600 / mi300 to make them available for reading
1. Open the hidden Menu of the inverter with http://<IP>/config_hide.html with Chrome (easiest with chrome)
2. Mark the IP-Adress Field under "Internal Server parameters setting"
    This Field normally has the AP-Adress 10.10.100.254 and is unable to edit
3. Click right Mousebutton and investigate Field
4. Delete the Text disabled="" from html-code
5. Click right Mousebutton oder Element in HTML and Force Status ":active"
6. Change IP to your internal inverter IP address
7. Click Save AND DON'T REBOOT
8. Wait some seconds and open http://<IP>/config_hide.html again to see if the changes had been saved. If not start again with 1
9. If IP is changed, you can restart the inverter, changes will be permanent
    

