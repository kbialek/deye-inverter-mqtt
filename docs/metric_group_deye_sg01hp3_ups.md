|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|
|---|---|:-:|:-:|:-:|:-:|:-:|
|Total Load Power|`ac/ups/total_power`|W|653|28d|U_WORD|1|
|Load L1 Power|`ac/ups/l1/power`|W|650|28a|S_WORD|1|
|Load L2 Power|`ac/ups/l2/power`|W|651|28b|S_WORD|1|
|Load L3 Power|`ac/ups/l3/power`|W|652|28c|S_WORD|1|
|Load Voltage L1|`ac/ups/l1/voltage`|V|644|284|U_WORD|0.1|
|Load Voltage L2|`ac/ups/l2/voltage`|V|645|285|U_WORD|0.1|
|Load Voltage L3|`ac/ups/l3/voltage`|V|646|286|U_WORD|0.1|
|Daily Load Consumption|`ac/ups/daily_energy`|kWh|526|20e|U_WORD|0.1|
|Total Load Consumption|`ac/ups/total_energy`|kWh|527,528|20f,210|U_DWORD (LW,HW)|0.1|
