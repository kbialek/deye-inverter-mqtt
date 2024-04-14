|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|
|---|---|:-:|:-:|:-:|:-:|:-:|
|Production today|`day_energy`|kWh|60|3c|U_WORD|0.1|
|Production Total|`total_energy`|kWh|63,64|3f,40|U_DWORD (LW,HW)|0.1|
|Phase1 Voltage|`ac/l1/voltage`|V|73|49|U_WORD|0.1|
|Phase1 Current|`ac/l1/current`|A|76|4c|U_WORD|0.1|
|Phase1 Power|`ac/l1/power`|W|computed|computed|n/a|1|
|Phase2 Voltage|`ac/l2/voltage`|V|74|4a|U_WORD|0.1|
|Phase2 Current|`ac/l2/current`|A|77|4d|U_WORD|0.1|
|Phase2 Power|`ac/l2/power`|W|computed|computed|n/a|1|
|Phase3 Voltage|`ac/l3/voltage`|V|75|4b|U_WORD|0.1|
|Phase3 Current|`ac/l3/current`|A|78|4e|U_WORD|0.1|
|Phase3 Power|`ac/l3/power`|W|computed|computed|n/a|1|
|AC Freq|`ac/freq`|Hz|79|4f|U_WORD|0.01|
|Uptime|`uptime`|minutes|62|3e|U_WORD|1|
|PV1 Voltage|`dc/pv1/voltage`|V|109|6d|U_WORD|0.1|
|PV1 Current|`dc/pv1/current`|A|110|6e|U_WORD|0.1|
|PV1 Power|`dc/pv1/power`|W|computed|computed|n/a|1|
|PV2 Voltage|`dc/pv2/voltage`|V|111|6f|U_WORD|0.1|
|PV2 Current|`dc/pv2/current`|A|112|70|U_WORD|0.1|
|PV2 Power|`dc/pv2/power`|W|computed|computed|n/a|1|
|PV3 Voltage|`dc/pv3/voltage`|V|113|71|U_WORD|0.1|
|PV3 Current|`dc/pv3/current`|A|114|72|U_WORD|0.1|
|PV3 Power|`dc/pv3/power`|W|computed|computed|n/a|1|
|PV4 Voltage|`dc/pv4/voltage`|V|115|73|U_WORD|0.1|
|PV4 Current|`dc/pv4/current`|A|116|74|U_WORD|0.1|
|PV4 Power|`dc/pv4/power`|W|computed|computed|n/a|1|
|DC Total Power|`dc/total_power`|W|82|52|U_WORD|0.1|
|Operating Power|`operating_power`|W|80|50|U_WORD|0.1|
|AC Apparent Power|`ac/apparent_power`|W|84|54|U_WORD|0.1|
|AC Active Power|`ac/active_power`|W|86,87|56,57|U_DWORD (LW,HW)|0.1|
|AC Reactive Power|`ac/reactive_power`|W|88|58|U_WORD|0.1|
|Radiator temperature|`radiator_temp`|°C|90|5a|U_WORD|0.1|
|IGBT temperature|`igbt_temp`|°C|91|5b|U_WORD|0.1|
