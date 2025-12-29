"""
This module handles the reading of all configured sensors.

It contains a main function `read_all_sensors` that iterates through the
SENSORS dictionary from `config.py`, calls the appropriate function for each
sensor type, and returns a list of readings.

To add support for a new sensor type, you need to:
1. Add a new `_read_<sensortype>` function.
2. This function should handle the hardware interaction.
3. It must return a list of dictionaries, where each dictionary represents
   a single value to be published via MQTT.
   e.g., [{'type': 'DHT11', 'data': {'id': ..., 'value': ...}}, ...]
4. Add a call to your new function in the `read_all_sensors` main loop.
"""

import time

from machine import Pin, ADC, I2C

# Import sensor-specific libraries with error handling
try:
    import dht
except ImportError:
    print("Warning: 'dht' library not found. DHT11 sensor will not work.")
    print("Install it using: import mip; mip.install('dht')")
    dht = None

try:
    import onewire
    import ds18x20
except ImportError:
    print(
        "Warning: 'onewire' or 'ds18x20' library not found. DS18B20 sensor will not work."
    )
    print("Install it using: import mip; mip.install('ds18x20')")
    onewire = None
    ds18x20 = None


# A simple MPU6050 library can be created or downloaded.
# For this example, we'll create a minimal one right here.
class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto(self.addr, b"\x6b\x00")  # Wake up the sensor

    def _read_word_2c(self, reg):
        val = self.i2c.readfrom_mem(self.addr, reg, 2)
        return val[0] << 8 | val[1]

    def get_values(self):
        raw_values = {
            "accel_x": self._read_word_2c(0x3B),
            "accel_y": self._read_word_2c(0x3D),
            "accel_z": self._read_word_2c(0x3F),
            "temp": self._read_word_2c(0x41),
            "gyro_x": self._read_word_2c(0x43),
            "gyro_y": self._read_word_2c(0x45),
            "gyro_z": self._read_word_2c(0x47),
        }

        # Convert to sensible values
        accel_x = self._convert_to_g(raw_values["accel_x"])
        accel_y = self._convert_to_g(raw_values["accel_y"])
        accel_z = self._convert_to_g(raw_values["accel_z"])
        temp = raw_values["temp"] / 340.0 + 36.53
        gyro_x = self._convert_to_dps(raw_values["gyro_x"])
        gyro_y = self._convert_to_dps(raw_values["gyro_y"])
        gyro_z = self._convert_to_dps(raw_values["gyro_z"])

        return {
            "accel_x": accel_x,
            "accel_y": accel_y,
            "accel_z": accel_z,
            "temp": temp,
            "gyro_x": gyro_x,
            "gyro_y": gyro_y,
            "gyro_z": gyro_z,
        }

    def _convert_to_g(self, raw):
        # Convert raw accelerometer data to 'g'
        return self._twos_complement(raw) / 16384.0

    def _convert_to_dps(self, raw):
        # Convert raw gyroscope data to degrees per second
        return self._twos_complement(raw) / 131.0

    @staticmethod
    def _twos_complement(val):
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val


# --- Sensor Reading Functions ---


def _read_dht11(config):
    if not dht:
        return []
    try:
        sensor = dht.DHT11(Pin(config["pin"]))
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        readings = [
            {
                "type": config["type"],
                "data": {
                    "id": config["provides"]["temperature"]["id"],
                    "value": temp,
                    "unit": config["provides"]["temperature"]["unit"],
                    "location": config["location"],
                    "active": config["active"],
                },
            },
            {
                "type": config["type"],
                "data": {
                    "id": config["provides"]["humidity"]["id"],
                    "value": hum,
                    "unit": config["provides"]["humidity"]["unit"],
                    "location": config["location"],
                    "active": config["active"],
                },
            },
        ]
        # Temperature reading
        # Humidity reading
        return readings
    except Exception as e:
        print(f"Error reading DHT11 sensor: {e}")
        return []


def _read_ds18b20_bus(config):
    if not onewire or not ds18x20:
        return []
    try:
        ow = onewire.OneWire(Pin(config["pin"]))
        time.sleep_ms(100)  # Speculative delay for bus to settle
        ds = ds18x20.DS18X20(ow)
        roms = ds.scan()
        ds.convert_temp()
        time.sleep_ms(750)

        readings = []
        for rom in roms:
            temp = ds.read_temp(rom)
            rom_id = "".join("{:02x}".format(x) for x in rom)
            sensor_id = (
                f"{config['provides']['temperature']['id_prefix']}_{rom_id[-4:]}"
            )

            readings.append(
                {
                    "type": config["type"],
                    "data": {
                        "id": sensor_id,
                        "value": temp,
                        "unit": config["provides"]["temperature"]["unit"],
                        "location": config["location"],
                        "active": config["active"],
                    },
                }
            )
        return readings
    except Exception as e:
        print(f"Error reading DS18B20 bus: {e}")
        return []


def _read_button(config):
    try:
        button = Pin(config["pin"], Pin.IN, Pin.PULL_UP)
        # Value is 0 if pressed, 1 if not pressed (due to PULL_UP)
        # We invert it to get a more intuitive boolean (True if pressed)
        value = not button.value()
        return [
            {
                "type": config["type"],
                "data": {
                    "id": config["provides"]["state"]["id"],
                    "value": value,
                    "unit": config["provides"]["state"]["unit"],
                    "location": config["location"],
                    "active": config["active"],
                },
            }
        ]
    except Exception as e:
        print(f"Error reading Button: {e}")
        return []


def _read_ldr(config):
    try:
        adc = ADC(Pin(config["pin"]))
        adc.init(sample_ns=50, atten=ADC.ATTN_11DB)
        value = adc.read_uv()
        return [
            {
                "type": config["type"],
                "data": {
                    "id": config["provides"]["light"]["id"],
                    "value": value,
                    "unit": config["provides"]["light"]["unit"],
                    "location": config["location"],
                    "active": config["active"],
                },
            }
        ]
    except Exception as e:
        print(f"Error reading LDR: {e}")
        return []


def _read_gy521(config):
    try:
        i2c = I2C(0, scl=Pin(config["scl_pin"]), sda=Pin(config["sda_pin"]))
        mpu = MPU6050(i2c)
        values = mpu.get_values()

        readings = []
        for key, value in values.items():
            sensor_config = config["provides"][key]
            readings.append(
                {
                    "type": config["type"],
                    "data": {
                        "id": sensor_config["id"],
                        "value": round(value, 2),
                        "unit": sensor_config["unit"],
                        "location": config["location"],
                        "active": config["active"],
                    },
                }
            )
        return readings
    except Exception as e:
        print(f"Error reading GY-521 (MPU6050): {e}")
        return []


# --- Main Function ---


def read_all_sensors():
    """
    Main function to read all sensors defined in config.py.

    Returns:
        A list of all sensor readings. Each reading is a dictionary
        formatted for publishing.
    """
    from config import SENSORS

    all_readings = []

    print("\n--- Reading all sensors ---")
    for sensor_name, config in SENSORS.items():
        if not config.get("active", False):
            continue

        print(f"Reading sensor: {sensor_name} ({config['type']})")

        if config["type"] == "DHT11":
            all_readings.extend(_read_dht11(config))
        elif config["type"] == "DS18B20":
            all_readings.extend(_read_ds18b20_bus(config))
        elif config["type"] == "Button":
            all_readings.extend(_read_button(config))
        elif config["type"] == "LDR":
            all_readings.extend(_read_ldr(config))
        elif config["type"] == "GY521":
            all_readings.extend(_read_gy521(config))
        # Add more 'elif' blocks here for other sensor types
        # elif config['type'] == 'SoilMoisture':
        #     all_readings.extend(_read_soil_moisture(config))
        else:
            print(
                f"Warning: No reader function implemented for sensor type '{config['type']}'"
            )

    print("--- Finished reading sensors ---")
    return all_readings
