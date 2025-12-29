# sensors.py
import time
from machine import Pin

try:
    import dht
except ImportError:
    dht = None

def _read_dht11(config):
    """Reads temperature and humidity from a DHT11 sensor."""
    if dht is None: return []
    
    try:
        sensor = dht.DHT11(Pin(config["pin"]))
        sensor.measure()
        time.sleep(1) # Stability delay
        
        readings = []
        # Add temperature reading
        readings.append({
            "type": "DHT11",
            "data": {
                "id": config["provides"]["temperature"]["id"],
                "value": sensor.temperature(),
                "unit": config["provides"]["temperature"]["unit"]
            }
        })
        # Add humidity reading
        readings.append({
            "type": "DHT11",
            "data": {
                "id": config["provides"]["humidity"]["id"],
                "value": sensor.humidity(),
                "unit": config["provides"]["humidity"]["unit"]
            }
        })
        return readings
    except Exception as e:
        print(f"DHT11 reading error on pin {config['pin']}: {e}")
        return []

def read_all_sensors():
    """Reads all sensors defined in config.py."""
    from config import SENSORS
    all_readings = []

    print("\n--- Reading indoor sensors ---")
    for name, cfg in SENSORS.items():
        if not cfg.get("active", False):
            continue

        if cfg["type"] == "DHT11":
            all_readings.extend(_read_dht11(cfg))
        # Add other sensor types (e.g., LDR or Button) if needed
            
    print("--- Finished reading sensors ---")
    return all_readings