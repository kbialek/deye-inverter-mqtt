DEFINITIONS = deye_sg04lp3 deye_hybrid deye_sg02lp1

DOWNLOAD_TARGETS = $(addprefix download-, $(DEFINITIONS))
IMPORT_TARGETS = $(addprefix import-, $(DEFINITIONS))

HA_DEFINITIONS_URL="https://raw.githubusercontent.com/StephanJoubert/home_assistant_solarman/main/custom_components/solarman/inverter_definitions"


$(DOWNLOAD_TARGETS): download-%:
	wget -q $(HA_DEFINITIONS_URL)/$*.yaml -O $*_ha.yaml

$(IMPORT_TARGETS): import-%:
	python ../tools/ha_definition_import.py \
		--definition-code $* \
		--sensors-file ../src/deye_sensors_$*.py