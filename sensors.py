# sensors.py
import time
from machine import Pin, ADC, I2C

# Import sensor-specific libraries with error handling
try:
    import onewire
    import ds18x20
except ImportError:
    onewire = None
    ds18x20 = None

def _read_ds18b20_bus(config):
    """Reads all DS18B20 sensors on a specific pin."""
    if onewire is None: return []
    
    readings = []
    pin = Pin(config["pin"])
    ds_bus = ds18x20.DS18X20(onewire.OneWire(pin))
    
    try:
        roms = ds_bus.scan()
        if not roms:
            print(f"No DS18B20 sensors found on pin {config['pin']}")
            return []
            
        ds_bus.convert_temp()
        time.sleep_ms(750) # Required conversion time
        
        for rom in roms:
            temp = ds_bus.read_temp(rom)
            if temp != 85.0: # Filter out power-on default value
                sensor_id = "".join("{:02x}".format(x) for x in rom)
                readings.append({
                    "type": "DS18B20",
                    "data": {
                        "id": config["provides"]["temperature"]["id_prefix"] + "_" + sensor_id,
                        "value": round(temp, 2),
                        "unit": config["provides"]["temperature"]["unit"]
                    }
                })
        return readings
    except Exception as e:
        print(f"DS18B20 reading error: {e}")
        return []

def read_all_sensors():
    """Reads all sensors defined as active in config.py."""
    from config import SENSORS
    all_readings = []

    print("\n--- Reading all sensors ---")
    for name, cfg in SENSORS.items():
        if not cfg.get("active", False):
            continue

        if cfg["type"] == "DS18B20":
            all_readings.extend(_read_ds18b20_bus(cfg))
        # Add more types here (DHT11, LDR, etc.)
            
    print("--- Finished reading sensors ---")
    return all_readings