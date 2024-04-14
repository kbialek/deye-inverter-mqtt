|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|
|---|---|:-:|:-:|:-:|:-:|:-:|
|PV1 Power|`dc/pv1/power`|W|672|2a0|U_WORD|10|
|PV2 Power|`dc/pv2/power`|W|673|2a1|U_WORD|10|
|PV3 Power|`dc/pv3/power`|W|674|2a2|U_WORD|10|
|PV4 Power|`dc/pv4/power`|W|675|2a3|U_WORD|10|
|PV1 Voltage|`dc/pv1/voltage`|V|676|2a4|U_WORD|0.1|
|PV1 Current|`dc/pv1/current`|A|677|2a5|U_WORD|0.1|
|PV2 Voltage|`dc/pv2/voltage`|V|678|2a6|U_WORD|0.1|
|PV2 Current|`dc/pv2/current`|A|679|2a7|U_WORD|0.1|
|PV3 Voltage|`dc/pv3/voltage`|V|680|2a8|U_WORD|0.1|
|PV3 Current|`dc/pv3/current`|A|681|2a9|U_WORD|0.1|
|PV4 Voltage|`dc/pv4/voltage`|V|682|2aa|U_WORD|0.1|
|PV4 Current|`dc/pv4/current`|A|683|2ab|U_WORD|0.1|
|Daily Production|`day_energy`|kWh|529|211|U_WORD|0.1|
|Total Production|`total_energy`|kWh|534,535|216,217|U_DWORD (LW,HW)|0.1|
|Total Grid Power|`ac/total_power`|W|625|271|S_WORD|1|
|Grid Voltage L1|`ac/l1/voltage`|V|598|256|U_WORD|0.1|
|Grid Voltage L2|`ac/l2/voltage`|V|599|257|U_WORD|0.1|
|Grid Voltage L3|`ac/l3/voltage`|V|600|258|U_WORD|0.1|
|Internal CT L1 Power|`ac/l1/ct/internal`|W|604|25c|S_WORD|1|
|Internal CT L2 Power|`ac/l2/ct/internal`|W|605|25d|S_WORD|1|
|Internal CT L3 Power|`ac/l3/ct/internal`|W|606|25e|S_WORD|1|
|External CT L1 Power|`ac/l1/ct/external`|W|616|268|S_WORD|1|
|External CT L2 Power|`ac/l2/ct/external`|W|617|269|S_WORD|1|
|External CT L3 Power|`ac/l3/ct/external`|W|618|26a|S_WORD|1|
|Daily Energy Bought|`ac/daily_energy_bought`|kWh|520|208|U_WORD|0.1|
|Total Energy Bought|`ac/total_energy_bought`|kWh|522,523|20a,20b|U_DWORD (LW,HW)|0.1|
|Daily Energy Sold|`ac/daily_energy_sold`|kWh|521|209|U_WORD|0.1|
|Total Energy Sold|`ac/total_energy_sold`|kWh|524,525|20c,20d|U_DWORD (LW,HW)|0.1|
|Current L1|`ac/l1/current`|A|630|276|S_WORD|0.01|
|Current L2|`ac/l2/current`|A|631|277|S_WORD|0.01|
|Current L3|`ac/l3/current`|A|632|278|S_WORD|0.01|
|Inverter L1 Power|`ac/l1/power`|W|633|279|S_WORD|1|
|Inverter L2 Power|`ac/l2/power`|W|634|27a|S_WORD|1|
|Inverter L3 Power|`ac/l3/power`|W|635|27b|S_WORD|1|
|DC Temperature|`radiator_temp`|°C|540|21c|S_WORD|0.1|
|AC Temperature|`ac/temperature`|°C|541|21d|S_WORD|0.1|
