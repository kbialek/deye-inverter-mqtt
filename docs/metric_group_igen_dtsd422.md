|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|
|---|---|:-:|:-:|:-:|:-:|:-:|
|Voltage CT1|`ct1/voltage`|V|1|1|U_WORD|0.1|
|Current CT1|`ct1/current`|A|7,8|7,8|SM_DWORD (LW,HW)|0.001|
|Active Power CT1|`ct1/active_power`|W|15,16|f,10|SM_DWORD (LW,HW)|1|
|Reactive Power CT1|`ct1/reactive_power`|Var|23,24|17,18|SM_DWORD (LW,HW)|1|
|Apparent Power CT1|`ct1/apparent_power`|VA|31,32|1f,20|SM_DWORD (LW,HW)|1|
|Power Factor CT1|`ct1/power_factor`||38|26|SM_WORD|0.001|
|Total Positive Energy CT1|`ct1/total_positive_energy`|kWh|62,63|3e,3f|U_DWORD (HW,LW)|0.01|
|Total Negative Energy CT1|`ct1/total_negative_energy`|kWh|72,73|48,49|U_DWORD (HW,LW)|0.01|
|Voltage CT2|`ct2/voltage`|V|2|2|U_WORD|0.1|
|Current CT2|`ct2/current`|A|9,10|9,a|SM_DWORD (LW,HW)|0.001|
|Active Power CT2|`ct2/active_power`|W|17,18|11,12|SM_DWORD (LW,HW)|1|
|Reactive Power CT2|`ct2/reactive_power`|Var|25,26|19,1a|SM_DWORD (LW,HW)|1|
|Apparent Power CT2|`ct2/apparent_power`|VA|33,34|21,22|SM_DWORD (LW,HW)|1|
|Power Factor CT2|`ct2/power_factor`||39|27|SM_WORD|0.001|
|Total Positive Energy CT2|`ct2/total_positive_energy`|kWh|82,83|52,53|U_DWORD (HW,LW)|0.01|
|Total Negative Energy CT2|`ct2/total_negative_energy`|kWh|92,93|5c,5d|U_DWORD (HW,LW)|0.01|
|Voltage CT3|`ct3/voltage`|V|3|3|U_WORD|0.1|
|Current CT3|`ct3/current`|A|11,12|b,c|SM_DWORD (LW,HW)|0.001|
|Active Power CT3|`ct3/active_power`|W|19,20|13,14|SM_DWORD (LW,HW)|1|
|Reactive Power CT3|`ct3/reactive_power`|Var|27,28|1b,1c|SM_DWORD (LW,HW)|1|
|Apparent Power CT3|`ct3/apparent_power`|VA|35,36|23,24|SM_DWORD (LW,HW)|1|
|Power Factor CT3|`ct3/power_factor`||40|28|SM_WORD|0.001|
|Total Positive Energy CT3|`ct3/total_positive_energy`|kWh|102,103|66,67|U_DWORD (HW,LW)|0.01|
|Total Negative Energy CT3|`ct3/total_negative_energy`|kWh|112,113|70,71|U_DWORD (HW,LW)|0.01|
|Voltage CT4|`ct4/voltage`|V|4097|1001|U_WORD|0.1|
|Current CT4|`ct4/current`|A|4103,4104|1007,1008|SM_DWORD (LW,HW)|0.001|
|Active Power CT4|`ct4/active_power`|W|4111,4112|100f,1010|SM_DWORD (LW,HW)|1|
|Reactive Power CT4|`ct4/reactive_power`|Var|4119,4120|1017,1018|SM_DWORD (LW,HW)|1|
|Apparent Power CT4|`ct4/apparent_power`|VA|4127,4128|101f,1020|SM_DWORD (LW,HW)|1|
|Power Factor CT4|`ct4/power_factor`||4134|1026|SM_WORD|0.001|
|Total Positive Energy CT4|`ct4/total_positive_energy`|kWh|4158,4159|103e,103f|U_DWORD (HW,LW)|0.01|
|Total Negative Energy CT4|`ct4/total_negative_energy`|kWh|4168,4169|1048,1049|U_DWORD (HW,LW)|0.01|
|Voltage CT5|`ct5/voltage`|V|4098|1002|U_WORD|0.1|
|Current CT5|`ct5/current`|A|4105,4106|1009,100a|SM_DWORD (LW,HW)|0.001|
|Active Power CT5|`ct5/active_power`|W|4113,4114|1011,1012|SM_DWORD (LW,HW)|1|
|Reactive Power CT5|`ct5/reactive_power`|Var|4121,4122|1019,101a|SM_DWORD (LW,HW)|1|
|Apparent Power CT5|`ct5/apparent_power`|VA|4129,4130|1021,1022|SM_DWORD (LW,HW)|1|
|Power Factor CT5|`ct5/power_factor`||4135|1027|SM_WORD|0.001|
|Total Positive Energy CT5|`ct5/total_positive_energy`|kWh|4178,4179|1052,1053|U_DWORD (HW,LW)|0.01|
|Total Negative Energy CT5|`ct5/total_negative_energy`|kWh|4188,4189|105c,105d|U_DWORD (HW,LW)|0.01|
|Voltage CT6|`ct6/voltage`|V|4099|1003|U_WORD|0.1|
|Current CT6|`ct6/current`|A|4107,4108|100b,100c|SM_DWORD (LW,HW)|0.001|
|Active Power CT6|`ct6/active_power`|W|4115,4116|1013,1014|SM_DWORD (LW,HW)|1|
|Reactive Power CT6|`ct6/reactive_power`|Var|4123,4124|101b,101c|SM_DWORD (LW,HW)|1|
|Apparent Power CT6|`ct6/apparent_power`|VA|4131,4132|1023,1024|SM_DWORD (LW,HW)|1|
|Power Factor CT6|`ct6/power_factor`||4136|1028|SM_WORD|0.001|
|Total Positive Energy CT6|`ct6/total_positive_energy`|kWh|4198,4199|1066,1067|U_DWORD (HW,LW)|0.01|
|Total Negative Energy CT6|`ct6/total_negative_energy`|kWh|4208,4209|1070,1071|U_DWORD (HW,LW)|0.01|
|Total Active Power (1st channel)|`total/1/active_power`|W|13,14|d,e|SM_DWORD (LW,HW)|1|
|Total Active Power (2nd channel)|`total/2/active_power`|W|4109,4110|100d,100e|SM_DWORD (LW,HW)|1|
|Total Reactive Power (1st channel)|`total/1/reactive_power`|Var|21,22|15,16|SM_DWORD (LW,HW)|1|
|Total Reactive Power (2nd channel)|`total/2/reactive_power`|Var|4117,4118|1015,1016|SM_DWORD (LW,HW)|1|
|Total Apparent Power (1st channel)|`total/1/apparent_power`|VA|29,30|1d,1e|SM_DWORD (LW,HW)|1|
|Total Apparent Power (2nd channel)|`total/2/apparent_power`|VA|4125,4126|101d,101e|SM_DWORD (LW,HW)|1|
|Total Positive Energy (1st channel)|`total/1/positive_energy`|kWh|42,43|2a,2b|U_DWORD (HW,LW)|0.01|
|Total Positive Energy (2nd channel)|`total/2/positive_energy`|kWh|4138,4139|102a,102b|U_DWORD (HW,LW)|0.01|
|Total Negative Energy (1st channel)|`total/1/negative_energy`|kWh|52,53|34,35|U_DWORD (HW,LW)|0.01|
|Total Negative Energy (2nd channel)|`total/2/negative_energy`|kWh|4148,4149|1034,1035|U_DWORD (HW,LW)|0.01|
|Power Factor (1st channel)|`total/1/power_factor`||37|25|SM_WORD|0.001|
|Power Factor (2nd channel)|`total/2/power_factor`||4133|1025|SM_WORD|0.001|
|Frequency (1st channel)|`total/1/frequency`|Hz|41|29|U_WORD|0.01|
|Frequency (2nd channel)|`total/2/frequency`|Hz|4137|1029|U_WORD|0.01|
