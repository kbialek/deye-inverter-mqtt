|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|
|---|---|:-:|:-:|:-:|:-:|:-:|
|PV1 Power|`dc/pv1/power`|W|186|ba|U_WORD|1|
|PV2 Power|`dc/pv2/power`|W|187|bb|U_WORD|1|
|PV1 Voltage|`dc/pv1/voltage`|V|109|6d|U_WORD|0.1|
|PV2 Voltage|`dc/pv2/voltage`|V|111|6f|U_WORD|0.1|
|PV1 Current|`dc/pv1/current`|A|110|6e|U_WORD|0.1|
|PV2 Current|`dc/pv2/current`|A|112|70|U_WORD|0.1|
|Daily Production|`day_energy`|kWh|108|6c|U_WORD|0.1|
|Total Production|`total_energy`|kWh|96,97|60,61|U_DWORD (LW,HW)|0.1|
|Micro-inverter Power|`micro_inverter_power`|W|166|a6|U_WORD|1|
|Total Grid Power|`ac/total_grid_power`|W|169|a9|S_WORD|1|
|Grid Voltage L1|`ac/l1/voltage`|V|150|96|U_WORD|0.1|
|Grid Voltage L2|`ac/l2/voltage`|V|151|97|U_WORD|0.1|
|Internal CT L1 Power|`ac/l1/ct/internal`|W|167|a7|S_WORD|1|
|Internal CT L2 Power|`ac/l2/ct/internal`|W|168|a8|S_WORD|1|
|External CT L1 Power|`ac/l1/ct/external`|W|170|aa|S_WORD|1|
|External CT L2 Power|`ac/l2/ct/external`|W|171|ab|S_WORD|1|
|Daily Energy Bought|`ac/daily_energy_bought`|kWh|76|4c|U_WORD|0.1|
|Total Energy Bought|`ac/total_energy_bought`|kWh|78,79|4e,4f|U_DWORD (LW,HW)|0.1|
|Daily Energy Sold|`ac/daily_energy_sold`|kWh|77|4d|U_WORD|0.1|
|Total Energy Sold|`ac/total_energy_sold`|kWh|81,82|51,52|U_DWORD (LW,HW)|0.1|
|Total Power|`ac/total_power`|W|175|af|S_WORD|1|
|Current L1|`ac/l1/current`|A|164|a4|S_WORD|0.01|
|Current L2|`ac/l2/current`|A|165|a5|S_WORD|0.01|
|Inverter L1 Power|`ac/l1/power`|W|173|ad|S_WORD|1|
|Inverter L2 Power|`ac/l2/power`|W|174|ae|S_WORD|1|
|Load Frequency|`ac/frequency`|Hz|192|c0|U_WORD|0.01|
|DC Temperature|`radiator_temp`|°C|90|5a|S_WORD|0.1|
|AC Temperature|`ac/temperature`|°C|91|5b|S_WORD|0.1|
