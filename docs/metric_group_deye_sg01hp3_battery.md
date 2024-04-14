|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|
|---|---|:-:|:-:|:-:|:-:|:-:|
|Daily Battery Charge|`battery/daily_charge`|kWh|514|202|U_WORD|0.1|
|Daily Battery Discharge|`battery/daily_discharge`|kWh|515|203|U_WORD|0.1|
|Total Battery Charge|`battery/total_charge`|kWh|516,517|204,205|U_DWORD (LW,HW)|0.1|
|Total Battery Discharge|`battery/total_discharge`|kWh|518,519|206,207|U_DWORD (LW,HW)|0.1|
|Battery1 Power|`battery/1/power`|W|590|24e|S_WORD|10|
|Battery1 Voltage|`battery/1/voltage`|V|587|24b|U_WORD|0.1|
|Battery1 SOC|`battery/1/soc`|%|588|24c|U_WORD|1|
|Battery1 Current|`battery/1/current`|A|591|24f|S_WORD|0.01|
|Battery1 Temperature|`battery/1/temperature`|°C|586|24a|U_WORD|0.1|
|Battery2 SOC|`battery/2/soc`|%|589|24d|U_WORD|1|
|Battery2 Voltage|`battery/2/voltage`|V|593|251|U_WORD|0.1|
|Battery2 Current|`battery/2/current`|A|594|252|S_WORD|0.01|
|Battery2 Power|`battery/2/power`|W|595|253|S_WORD|10|
|Battery2 Temperature|`battery/2/temperature`|°C|596|254|S_WORD|0.1|
