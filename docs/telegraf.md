# Example usage with [telegraf]

You can use this project in combination with [telegraf] or similar tools to get
your inverter's data into other systems than mqtt.

An example usage with [telegraf] could look something like that:
- disable the mqtt publisher
- enable the stdout publisher
- ensure all logs go to stderr instead of stdout
- run `deye-inverter-mqtt` as an `execd` plugin via telegraf

This can be achived with a telegraf config file like that:
```
[[outputs.file]]
  files = ["stdout"]
  # data_format = "prometheus"
  data_format = "influx"

[[inputs.execd]]
  command = ["python", "deye_docker_entrypoint.py"]
  environment = [
    "DEYE_LOGGER_IP_ADDRESS=192.168.0.254",
    "DEYE_LOGGER_PORT=8899",
    "DEYE_LOGGER_SERIAL_NUMBER=123412341234",
    "LOG_LEVEL=INFO",
    "LOG_STREAM=STDERR",
    "DEYE_FEATURE_MQTT_PUBLISHER=false",
    "DEYE_FEATURE_STDOUT_PUBLISHER=true",
    "DEYE_FEATURE_SET_TIME=false",
    "DEYE_METRIC_GROUPS=micro",
  ]

  # command = [
  #   "docker",
  #   "run",
  #   "-e", "DEYE_LOGGER_IP_ADDRESS=192.168.0.254",
  #   "-e", "DEYE_LOGGER_PORT=8899",
  #   "-e", "DEYE_LOGGER_SERIAL_NUMBER=123412341234",
  #   "-e", "LOG_LEVEL=INFO",
  #   "-e", "LOG_STREAM=STDERR",
  #   "-e", "DEYE_FEATURE_MQTT_PUBLISHER=false",
  #   "-e", "DEYE_FEATURE_STDOUT_PUBLISHER=true",
  #   "-e", "DEYE_FEATURE_SET_TIME=false",
  #   "-e", "DEYE_METRIC_GROUPS=micro",
  #   "ghcr.io/kbialek/deye-inverter-mqtt",
  # ]

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
      tags = ["name", "groups", "sensor", "unit"]
```

This would produce the following metrics in the `influx` format on stdout:
```
deye,address=192.168.0.254,host=pfah,port=8899,serial=123412341234 up=1 1685797625572131092
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Production\ today,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=kWh day_energy=1.3 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Production\ Total,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,unit=kWh total_energy=5.5 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Phase1\ Voltage,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=V ac/l1/voltage=238 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Phase1\ Current,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=A ac/l1/current=1.3 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Phase1\ Power,port=8899,sensor=ComputedPowerSensor,serial=123412341234,unit=W ac/l1/power=309.40000000000003 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=AC\ Freq,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=Hz ac/freq=50 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Uptime,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=minutes uptime=0 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV1\ Voltage,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=V dc/pv1/voltage=25.3 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV1\ Current,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=A dc/pv1/current=1.5 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV1\ Power,port=8899,sensor=ComputedPowerSensor,serial=123412341234,unit=W dc/pv1/power=37.95 1685797625571284000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV1\ Production\ today,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=kWh dc/pv1/day_energy=0.8 1685797625571284000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV1\ Total,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,unit=kWh dc/pv1/total_energy=4.9 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV2\ Voltage,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=V dc/pv2/voltage=26.5 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV2\ Current,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=A dc/pv2/current=10.4 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV2\ Power,port=8899,sensor=ComputedPowerSensor,serial=123412341234,unit=W dc/pv2/power=275.6 1685797625571284000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV2\ Production\ today,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=kWh dc/pv2/day_energy=0.4 1685797625571284000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV2\ Total,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,unit=kWh dc/pv2/total_energy=0.5 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV3\ Voltage,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=V dc/pv3/voltage=0 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV3\ Current,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=A dc/pv3/current=0 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV3\ Power,port=8899,sensor=ComputedPowerSensor,serial=123412341234,unit=W dc/pv3/power=0 1685797625571284000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV3\ Production\ today,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=kWh dc/pv3/day_energy=0 1685797625571284000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV3\ Total,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,unit=kWh dc/pv3/total_energy=0 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV4\ Voltage,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=V dc/pv4/voltage=0 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV4\ Current,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=A dc/pv4/current=0 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=PV4\ Power,port=8899,sensor=ComputedPowerSensor,serial=123412341234,unit=W dc/pv4/power=0 1685797625571284000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV4\ Production\ today,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=kWh dc/pv4/day_energy=0 1685797625571284000
deye,address=192.168.0.254,groups=micro,host=pfah,name=PV4\ Total,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,unit=kWh dc/pv4/total_energy=0 1685797625571284000
deye,address=192.168.0.254,groups=micro,host=pfah,name=DC\ Total\ Power,port=8899,sensor=ComputedSumSensor,serial=123412341234,unit=W dc/total_power=313.55 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=Operating\ Power,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=W operating_power=0 1685797625571284000
deye,address=192.168.0.254,groups=string\,micro,host=pfah,name=AC\ Active\ Power,port=8899,sensor=DoubleRegisterSensor,serial=123412341234,unit=W ac/active_power=315 1685797625571284000
deye,address=192.168.0.254,groups=micro,host=pfah,name=Radiator\ temperature,port=8899,sensor=SingleRegisterSensor,serial=123412341234,unit=°C radiator_temp=47.300000000000004 1685797625571284000
```

Of course, the output plugin here is just an example. You can process and
output the metrics in whatever format the tool in question, here telegraf,
supports.

[telegraf]: https://github.com/influxdata/telegraf
