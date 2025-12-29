# main.py
import time
import machine
import wifi  # Übernimmt die LED-Erkennung (GPIO 2 für einfache LED)
import ntp
from mqtt_client import MQTT
from sensors import read_all_sensors

# --- Konfiguration ---
LOOP_INTERVAL_SEC = 900  # 1 Minute für den Test, später auf 900 (15 Min) hochstellen


def main():
    print("--- ESP32-C3 Sensor-Station Start ---")

    # 1. WiFi verbinden
    # wifi.connect() nutzt deine StatusLed Klasse für GPIO 2
    try:
        if not wifi.connect():
            print("WiFi Verbindung fehlgeschlagen.")
            return
    except Exception as e:
        print(f"Kritischer WiFi Fehler: {e}")
        time.sleep(10)
        machine.reset()

    # 2. Zeit synchronisieren
    try:
        ntp.sync_time()
    except Exception as e:
        print(f"Zeit-Sync fehlgeschlagen: {e}")

    # 3. MQTT initialisieren
    mqtt = None
    try:
        mqtt = MQTT()
        if not mqtt.connect():
            print("MQTT Broker nicht erreichbar!")
            return

        print("\n--- Starte Sensor-Schleife ---")
        while True:
            # 1. Verbindung prüfen & ggf. reconnect
            if not mqtt.is_connected:
                print("MQTT Verbindung verloren. Reconnect...")
                mqtt.connect()

            # --- AB HIER: Wieder auf der richtigen Ebene einrücken! ---

            # 2. Sensoren auslesen (Immer ausführen, wenn verbunden)
            sensor_readings = read_all_sensors()

            if sensor_readings:
                # Blaues Licht (RGB) oder AN (Einfache LED) während des Sendens
                wifi.led.set_state(0, 0, 255)

                for reading in sensor_readings:
                    data = reading["data"]
                    # WICHTIG: Prüfe, ob deine mqtt_client.py "topic" als Argument akzeptiert
                    mqtt.publish(data, topic="Sensors")

                    print(f"Gesendet: Sensors -> {data['id']}: {data['value']} {data['unit']}")
                    time.sleep(0.5)

                wifi.led.set_state(0, 0, 0)  # LED wieder aus
            else:
                print("Keine Sensoren zum Auslesen gefunden.")

            # 3. Warten bis zum nächsten Zyklus
            print(f"--- Zyklus beendet. Warte {LOOP_INTERVAL_SEC} Sek. ---")
            time.sleep(LOOP_INTERVAL_SEC)

    except KeyboardInterrupt:
        print("Manuell gestoppt.")
    except Exception as e:
        print(f"Fehler im Hauptprogramm: {e}")
        time.sleep(10)
        machine.reset()
    finally:
        if mqtt:
            mqtt.disconnect()


if __name__ == "__main__":
    main()
