# Overview

The community behind https://github.com/StephanJoubert/home_assistant_solarman project did the hard work and crafted modbus registry mappings for various types of inverters.

Let's reuse the great work they've done, and import their registry mappings into this project.

# How to import a new definition
1. Go to https://github.com/StephanJoubert/home_assistant_solarman/tree/main/custom_components/solarman/inverter_definitions
2. Pick the name to import, e.g. `deye_sg04lp3`
3. In the Makefile, add this name to `DEFINITIONS` variable
4. Define `deye_sg04lp3_map.yaml` file that will
    1. Map registers to mqtt topics
    2. Map register groups to metrics groups
5. Run `make download-deye_sg04lp3` to download the definition
5. Run `make import-deye_sg04lp3` to generate a python sensors file


