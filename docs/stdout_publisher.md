# Using the stdout publisher

Enabling this with `DEYE_FEATURE_STDOUT_PUBLISHER` will dump all collected
metrics in json on stdout once every cycle (every `DEYE_DATA_READ_INTERVAL`
seconds).
This can be useful in combination with other tools to process and push the
metrics into different systems other than mqtt.

The json object has the following structure:
```json
{
  "serial": "1234567890",
  "address": "192.168.0.1",
  "port": 8899,
  "data": [
    {
      "up": 1,
    }, {
      "temp": 31,
      "name": "Radiator temperature",
      "unit": "°C",
      "groups": "micro",
      "sensor": "SingleRegisterSensor",
      "source": "radiator",
      "timestamp": 1686219130
    }, {
      "energy": 0.2,
      "name": "PV1 Total",
      "unit": "kWh",
      "groups": "micro",
      "sensor": "DoubleRegisterSensor",
      "source": "dc/pv1/total",
      "timestamp": 1686219130
    }, {
      ...
    }
  ]
}
```

## Example usage with [telegraf]

To collect the inverter metric with telegraf and then process or push them
forward you can run `deye-inverter-mqtt` with the following configuration:
- disable the mqtt publisher
- enable the stdout publisher
- ensure all logs go to stderr instead of stdout

This can be achieved with a telegraf config file like that:
```
[[outputs.file]]
  files = ["stdout"]
  data_format = "influx"

[[inputs.execd]]
  command = [
    "docker",
    "run",
    "-e", "DEYE_LOGGER_IP_ADDRESS=192.168.0.254",
    "-e", "DEYE_LOGGER_PORT=8899",
    "-e", "DEYE_LOGGER_SERIAL_NUMBER=123412341234",
    "-e", "LOG_LEVEL=INFO",
    "-e", "LOG_STREAM=STDERR",
    "-e", "DEYE_FEATURE_MQTT_PUBLISHER=false",
    "-e", "DEYE_FEATURE_STDOUT_PUBLISHER=true",
    "-e", "DEYE_FEATURE_SET_TIME=false",
    "-e", "DEYE_METRIC_GROUPS=micro",
    "ghcr.io/kbialek/deye-inverter-mqtt",
  ]

  signal = "none"
  restart_delay = "10s"

  data_format = "json_v2"
  [[inputs.execd.json_v2]]
    measurement_name = "deye"
    [[inputs.execd.json_v2.tag]]
      path = "serial"
    [[inputs.execd.json_v2.tag]]
      path = "address"
    [[inputs.execd.json_v2.tag]]
      path = "port"
    [[inputs.execd.json_v2.object]]
      path = "data"
      timestamp_key = "timestamp"
      timestamp_format = "unix"
      tags = ["name", "groups", "sensor", "unit", "source"]
```

This would produce the following metrics in the `influx` format on stdout:
```
deye,address=192.168.0.254,host=pfah,port=8899,serial=123412341234 up=1 1685867801610059060
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Production\ today,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=day,unit=kWh energy=0.1 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Production\ Total,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,source=total,unit=kWh energy=5.800000000000001 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Phase1\ Voltage,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=ac/l1,unit=V voltage=235 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Phase1\ Current,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=ac/l1,unit=A current=0.2 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Phase1\ Power,port=8899,sensor=ComputedPowerSensor,serial=123412341234,source=ac/l1,unit=W power=47 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=AC\ Freq,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=ac,unit=Hz freq=50.1 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Uptime,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=minutes uptime=0 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV1\ Voltage,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv1,unit=V voltage=29.5 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV1\ Current,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv1,unit=A current=1.3 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV1\ Power,port=8899,sensor=ComputedPowerSensor,serial=123412341234,source=dc/pv1,unit=W power=38.35 1685867801000000000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV1\ Production\ today,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv1/day,unit=kWh energy=0 1685867801000000000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV1\ Total,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,source=dc/pv1/total,unit=kWh energy=5 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV2\ Voltage,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv2,unit=V voltage=28.900000000000002 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV2\ Current,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv2,unit=A current=0.8 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV2\ Power,port=8899,sensor=ComputedPowerSensor,serial=123412341234,source=dc/pv2,unit=W power=23.120000000000005 1685867801000000000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV2\ Production\ today,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv2/day,unit=kWh energy=0 1685867801000000000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV2\ Total,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,source=dc/pv2/total,unit=kWh energy=0.6000000000000001 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV3\ Voltage,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv3,unit=V voltage=0 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV3\ Current,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv3,unit=A current=0 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV3\ Power,port=8899,sensor=ComputedPowerSensor,serial=123412341234,source=dc/pv3,unit=W power=0 1685867801000000000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV3\ Production\ today,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv3/day,unit=kWh energy=0 1685867801000000000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV3\ Total,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,source=dc/pv3/total,unit=kWh energy=0 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV4\ Voltage,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv4,unit=V voltage=0 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV4\ Current,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv4,unit=A current=0 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV4\ Power,port=8899,sensor=ComputedPowerSensor,serial=123412341234,source=dc/pv4,unit=W power=0 1685867801000000000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV4\ Production\ today,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=dc/pv4/day,unit=kWh energy=0 1685867801000000000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV4\ Total,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,source=dc/pv4/total,unit=kWh energy=0 1685867801000000000
deye,address=192.168.0.254,groups=micro,host=pfah,name=DC\ Total\ Power,port=8899,sensor=ComputedSumSensor,serial=123412341234,source=dc/total,unit=W power=61.470000000000006 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Operating\ Power,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=operating,unit=W power=0 1685867801000000000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=AC\ Active\ Power,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,source=ac/active,unit=W power=64 1685867801000000000
deye,address=192.168.0.254,groups=micro,host=pfah,name=Radiator\ temperature,port=8899,sensor=SingleRegisterSensor,serial=123412341234,source=radiator,unit=°C temp=26 1685867801000000000
```

Of course, the output plugin here is just an example. You can process and
output the metrics with whatever plugins telegraf supports.

[telegraf]: https://github.com/influxdata/telegraf
