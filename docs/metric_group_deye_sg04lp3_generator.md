|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|
|---|---|:-:|:-:|:-:|:-:|:-:|
|Phase voltage of Gen port A|`ac/generator/a/voltage`|V|661|295|U_WORD|0.1|
|Phase voltage of Gen port B|`ac/generator/b/voltage`|V|662|296|U_WORD|0.1|
|Phase voltage of Gen port C|`ac/generator/c/voltage`|V|663|297|U_WORD|0.1|
|Phase power of Gen port A|`ac/generator/a/power`|W|664|298|U_WORD|1|
|Phase power of Gen port B|`ac/generator/b/power`|W|665|299|U_WORD|1|
|Phase power of Gen port C|`ac/generator/c/power`|W|666|29a|U_WORD|1|
|Total Power of Gen Ports|`ac/generator/total_power`|W|667|29b|U_WORD|1|
|Daily Generator Production|`ac/generator/daily_energy`|kWh|536|218|U_WORD|0.1|
