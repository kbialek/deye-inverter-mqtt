|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|
|---|---|:-:|:-:|:-:|:-:|:-:|
|Daily Battery Charge|`battery/daily_charge`|kWh|514|202|U_WORD|0.1|
|Daily Battery Discharge|`battery/daily_discharge`|kWh|515|203|U_WORD|0.1|
|Total Battery Charge|`battery/total_charge`|kWh|516,517|204,205|U_DWORD (LW,HW)|0.1|
|Total Battery Discharge|`battery/total_discharge`|kWh|518,519|206,207|U_DWORD (LW,HW)|0.1|
|Battery Power|`battery/power`|W|590|24e|S_WORD|1|
|Battery Voltage|`battery/voltage`|V|587|24b|U_WORD|0.01|
|Battery SOC|`battery/soc`|%|588|24c|U_WORD|1|
|Battery Current|`battery/current`|A|591|24f|S_WORD|0.01|
|Battery Temperature|`battery/temperature`|°C|586|24a|U_WORD|0.1|
