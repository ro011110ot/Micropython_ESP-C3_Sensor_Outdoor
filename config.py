# config.py

# Pin for the onboard status LED (if available)
STATUS_LED_PIN = 2

# --- Sensor Configuration ---
# This dictionary defines all the sensors connected to the ESP32.
# Each key is a unique name for the sensor.
#
# The following properties are supported:
# - 'type': The type of the sensor (e.g., 'DHT11', 'DS18B20', 'Button', 'LDR', 'GY521').
# - 'active': Set to True to enable the sensor, False to disable it.
# - 'pin': The GPIO number the sensor is connected to.
# - 'scl_pin', 'sda_pin': For I2C sensors like the GY521.
# - 'location': A string describing the sensor's location (e.g., 'Living Room').
# - 'provides': A dictionary describing the values the sensor provides.
#   - Each key is the type of value (e.g., 'temperature', 'humidity', 'state').
#   - 'id': The unique ID for this specific value, used in the MQTT message.
#   - 'unit': The unit of measurement (e.g., '°C', '%').
#   - 'id_prefix': For DS18B20 buses, a prefix for the unique sensor IDs.

SENSORS = {
    "dht11_living_room": {
        "type": "DHT11",
        "active": False,
        "pin": 2,
        "location": "Living Room",
        "provides": {
            "temperature": {"id": "Sensor_DHT11_Temp", "unit": "°C"},
            "humidity": {"id": "Sensor_DHT11_Hum", "unit": "%"},
        },
    },
    "ds18b20_aussen": {
        "type": "DS18B20",
        "active": True,
        "pin": 4,
        "location": "Aussen",
        "provides": {"temperature": {"id_prefix": "Sensor_DS18B20", "unit": "C"}},
    },
    "button_1": {
        "type": "Button",
        "active": False,  # Disabled for now
        "pin": 21,
        "location": "Living Room",
        "provides": {"state": {"id": "Sensor_Button_1", "unit": "boolean"}},
    },
    "ldr_1": {
        "type": "LDR",
        "active": False,  # Disabled for now
        "pin": 34,
        "location": "Living Room",
        "provides": {"light": {"id": "Sensor_LDR_1", "unit": "uv"}},
    },
    "gy521_1": {
        "type": "GY521",
        "active": False,  # Disabled for now
        "scl_pin": 19,
        "sda_pin": 18,
        "location": "Living Room",
        "provides": {
            "accel_x": {"id": "Sensor_GY521_AccelX", "unit": "g"},
            "accel_y": {"id": "Sensor_GY521_AccelY", "unit": "g"},
            "accel_z": {"id": "Sensor_GY521_AccelZ", "unit": "g"},
            "temp": {"id": "Sensor_GY521_Temp", "unit": "°C"},
            "gyro_x": {"id": "Sensor_GY521_GyroX", "unit": "dps"},
            "gyro_y": {"id": "Sensor_GY521_GyroY", "unit": "dps"},
            "gyro_z": {"id": "Sensor_GY521_GyroZ", "unit": "dps"},
        },
    },
}
