|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|
|---|---|:-:|:-:|:-:|:-:|:-:|
|Total Battery Charge|`battery/total_charge`|kWh|72,73|48,49|U_DWORD (LW,HW)|0.1|
|Total Battery Discharge|`battery/total_discharge`|kWh|74,75|4a,4b|U_DWORD (LW,HW)|0.1|
|Daily Battery Charge|`battery/daily_charge`|kWh|70|46|U_WORD|0.1|
|Daily Battery Discharge|`battery/daily_discharge`|kWh|71|47|U_WORD|0.1|
|Battery Status|`battery/status`||189|bd|U_WORD|1|
|Battery Power|`battery/power`|W|190|be|S_WORD|1|
|Battery Voltage|`battery/voltage`|V|183|b7|U_WORD|0.01|
|Battery SOC|`battery/soc`|%|184|b8|U_WORD|1|
|Battery Current|`battery/current`|A|191|bf|S_WORD|0.01|
|Battery Temperature|`battery/temperature`|°C|182|b6|U_WORD|0.1|
