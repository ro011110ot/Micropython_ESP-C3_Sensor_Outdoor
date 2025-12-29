import network
import time
import ubinascii
from secrets import WIFI_CREDENTIALS

# --- Dynamische LED Erkennung ---
led = None

try:
    from status_led_rgb import StatusLedRGB

    led = StatusLedRGB()
    print("RGB LED erkannt.")
except ImportError:
    try:
        from status_led import StatusLed

        led = StatusLed()
        print("Einfache LED erkannt.")
    except ImportError:

        class DummyLed:
            def wifi_connecting(self):
                pass

            def mqtt_connecting(self):
                pass

            def set_state(self, r, g, b):
                pass

            def off(self):
                pass

        led = DummyLed()
        print("Keine Status-LED Datei gefunden. Fahre ohne LED fort.")


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # MAC-Adresse auslesen und formatieren
    mac = ubinascii.hexlify(wlan.config("mac"), ":").decode()

    for creds in WIFI_CREDENTIALS:
        wlan.disconnect()
        time.sleep(1)

        ssid = creds.get("ssid")
        password = creds.get("password")

        print(f"Verbinde mit {ssid}...")
        wlan.connect(ssid, password)

        max_wait = 10
        while max_wait > 0:
            led.wifi_connecting()
            if wlan.isconnected():
                break
            max_wait -= 1
            time.sleep(1)

        if wlan.isconnected():
            # Netzwerk-Konfiguration abrufen (IP, Subnet, Gateway, DNS)
            config = wlan.ifconfig()
            ip_address = config[0]

            print("-" * 30)
            print("WLAN erfolgreich verbunden!")
            print(f"SSID: {ssid}")
            print(f"IP-Adresse:  {ip_address}")
            print(f"MAC-Adresse: {mac.upper()}")
            print("-" * 30)

            # LED auf Grün (oder AN) setzen
            led.set_state(0, 255, 0)
            return True  # <--- HIER MUSS TRUE STEHEN!

    if not wlan.isconnected():
        led.set_state(255, 0, 0)  # Rot bei RGB, AN bei einfacher LED
        print(f"Fehler: Verbindung zu keinem Netzwerk möglich. MAC: {mac.upper()}")
        raise RuntimeError("Netzwerkverbindung fehlgeschlagen")
    return False
