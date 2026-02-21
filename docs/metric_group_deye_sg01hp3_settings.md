|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|
|---|---|:-:|:-:|:-:|:-:|:-:|
|Maximum battery charge current|`settings/battery/maximum_charge_current`|A|108|6c|U_WORD|1|
|Maximum battery discharge current|`settings/battery/maximum_discharge_current`|A|109|6d|U_WORD|1|
|Maximum battery_grid charge current|`settings/battery/maximum_grid_charge_current`|A|128|80|U_WORD|1|
|Grid Charge enabled|`settings/battery/grid_charge`|Bit {0,1}|130|82|U_WORD|1|
|Work Mode|`settings/workmode`||142|8e|U_WORD|1|
|Max Solar Sell Power|`settings/solar_sell_max_power`|W|143|8f|U_WORD|10|
|Solar sell enabled|`settings/solar_sell`|Bit {0,1}|145|91|U_WORD|1|
