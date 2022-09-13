# Deye solar inverter MQTT bridge

Reads Deye solar inverter metrics and posts them over MQTT.

Tested with [Deye SUN-4K-G05](https://www.deyeinverter.com/product/three-phase-string-inverter/sun4-5-6-7-8-10kg03.html) and Logger S/N 23xxxxxxxx

Supported metrics:

|Metric|Modbus address|MQTT topic suffix|Unit|
|---|:-:|---|:-:|
|Production today|0x3c|`day_energy`|kWh|
|Uptime|0x3e|`uptime`|minutes|
|AC Phase 1 voltage|0x49|`ac/l1/voltage`|V|
|AC Phase 2 voltage|0x4a|`ac/l2/voltage`|V|
|AC Phase 3 voltage|0x4b|`ac/l3/voltage`|V|
|AC Phase 1 current|0x4c|`ac/l1/current`|A|
|AC Phase 2 current|0x4d|`ac/l2/current`|A|
|AC Phase 3 current|0x4e|`ac/l3/current`|A|
|AC Frequency|0x4f|`ac/freq`|Hz|
|Operating power|0x50|`operating_power`|W|
|DC total power|0x52|`dc/total_power`|W|
|AC apparent power|0x54|`ac/apparent_power`|W|
|AC active power|0x56|`ac/active_power`|W|
|AC reactive power|0x58|`ac/reactive_power`|W|
|Radiator temperature|0x5a|`radiator_temp`|C|
|IGBT temperature|0x5b|`igbt_temp`|C|
|DC PV1 voltage|0x6d|`dc/pv1/voltage`|V|
|DC PV1 current|0x6e|`dc/pv1/current`|A|
|DC PV2 voltage|0x6f|`dc/pv2/voltage`|V|
|DC PV2 current|0x70|`dc/pv2/current`|A|


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
* `DEYE_LOGGER_SERIAL_NUMBER` - inverter data logger serial number
* `DEYE_LOGGER_IP_ADDRESS` - inverter data logger IP address
* `DEYE_LOGGER_PORT` - inverter data logger communication port, typically 8899
* `MQTT_HOST`
* `MQTT_PORT`
* `MQTT_USERNAME`
* `MQTT_PASSWORD`
* `MQTT_TOPIC_PREFIX` - mqtt topic prefix used for all inverter metrics



