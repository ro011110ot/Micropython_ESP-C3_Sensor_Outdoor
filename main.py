# main.py
import time
import machine
import wifi
import ntp
import gc
from mqtt_client import MQTT
from sensors import read_all_sensors

# --- Configuration ---
LOOP_INTERVAL_SEC = 900  # 15 minutes cycle


def main():
    print("--- ESP32-C3 Sensor Station Starting ---")

    # 1. Connect to WiFi
    try:
        if not wifi.connect():
            print("WiFi connection failed. Resetting...")
            time.sleep(10)
            machine.reset()
    except Exception as e:
        print(f"Critical WiFi error: {e}")
        time.sleep(10)
        machine.reset()

    # 2. Synchronize Time
    try:
        ntp.sync()  # Updated to match your ntp.py function name
    except Exception as e:
        print(f"Time synchronization failed: {e}")

    # 3. Initialize MQTT
    mqtt = MQTT()
    if not mqtt.connect():
        print("MQTT Broker unreachable! Retrying in 30s...")
        time.sleep(30)
        machine.reset()

    print("\n--- Starting Main Sensor Loop ---")

    while True:
        try:
            # Check connection and reconnect if necessary
            if not mqtt.is_connected:
                print("MQTT connection lost. Reconnecting...")
                mqtt.connect()

            # Read all sensors configured in config.py
            sensor_readings = read_all_sensors()

            if sensor_readings:
                # Optional: Indicate activity via LED if available
                if hasattr(wifi, 'led'):
                    wifi.led.set_state(0, 0, 255)  # Blue for transmission

                for reading in sensor_readings:
                    # 'reading' is a dict like {'type': 'DS18B20', 'data': {...}}
                    payload = reading["data"]

                    # Publish to the 'Sensors' topic
                    if mqtt.publish(payload, topic="Sensors"):
                        print(f"Published: {payload['id']} -> {payload['value']} {payload['unit']}")

                    time.sleep(0.5)  # Short delay between messages

                if hasattr(wifi, 'led'):
                    wifi.led.set_state(0, 0, 0)  # LED off
            else:
                print("No active sensors found or all readings failed.")

            print(f"--- Cycle finished. Waiting {LOOP_INTERVAL_SEC} sec ---")

            # Clean up memory
            gc.collect()
            time.sleep(LOOP_INTERVAL_SEC)

        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(10)
            gc.collect()


if __name__ == "__main__":
    main()