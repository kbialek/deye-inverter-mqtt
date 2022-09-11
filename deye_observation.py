from deye_sensor import Sensor

class Observation():
    """
    Models Solar Inverter sensor reading.
    """

    def __init__(self, sensor: Sensor, timestamp, value):
        self.sensor = sensor
        self.timestamp = timestamp
        self.value = value

    def value_as_str(self):
        return self.sensor.format_value(self.value)


