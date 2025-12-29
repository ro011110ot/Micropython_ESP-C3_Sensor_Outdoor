# main.py
import time
import machine
import wifi
import ntp
import gc
import json
from mqtt_client import MQTT
from sensors import read_all_sensors

# --- Configuration ---
# 900 seconds = 15 minutes for battery efficiency
LOOP_INTERVAL_SEC = 900


def main():
    print("--- ESP32-C3 Outdoor Sensor Station Starting ---")

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

    # 2. Synchronize Time (Important for SSL)
    try:
        ntp.sync()
    except Exception as e:
        print(f"Time synchronization failed: {e}")

    # 3. Initialize MQTT
    mqtt = MQTT()
    if not mqtt.connect():
        print("MQTT Broker unreachable! Retrying in 30s...")
        time.sleep(30)
        machine.reset()

    print("\n--- Starting Main Outdoor Loop ---")

    while True:
        try:
            # Check connection and reconnect if necessary
            if not mqtt.is_connected:
                print("MQTT connection lost. Reconnecting...")
                mqtt.connect()

            # Read all sensors configured in sensors.py
            sensor_readings = read_all_sensors()

            if sensor_readings:
                # Indicate activity via LED if available
                if hasattr(wifi, 'led'):
                    wifi.led.set_state(0, 0, 255)

                for reading in sensor_readings:
                    # 'payload' contains id, value, unit
                    payload = reading["data"]

                    # DYNAMIC TOPIC: Creates 'Sensors/Outdoor/Temp' etc.
                    # This ensures the MariaDB Logger creates separate tables.
                    topic_suffix = reading.get('type', 'Unknown')
                    specific_topic = f"Sensors/Outdoor/{topic_suffix}"

                    print(f"Attempting to publish to {specific_topic}...")

                    # Publish as JSON with Retain-Flag
                    if mqtt.publish(payload, topic=specific_topic, retain=True):
                        print(f"Success: {json.dumps(payload)}")
                    else:
                        print(f"FAILED to publish to {specific_topic}")

                    # CRITICAL: Wait 2 seconds between SSL packets!
                    # The ESP32-C3 needs time to process encryption for each message.
                    time.sleep(2)

                if hasattr(wifi, 'led'):
                    wifi.led.set_state(0, 0, 0)
            else:
                print("No active sensors found or all readings failed.")

            print(f"--- Cycle finished. Next reading in {LOOP_INTERVAL_SEC}s ---")

            # Clean up memory to prevent crashes
            gc.collect()
            time.sleep(LOOP_INTERVAL_SEC)

        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(10)
            gc.collect()


if __name__ == "__main__":
    main()