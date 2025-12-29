# wifi.py
import time
import network
import ubinascii
from secrets import WIFI_CREDENTIALS

# --- Dynamic LED Detection ---
led = None
try:
    from status_led_rgb import StatusLedRGB
    led = StatusLedRGB()
    print("RGB LED detected.")
except ImportError:
    try:
        from status_led import StatusLed
        led = StatusLed()
        print("Simple LED detected.")
    except ImportError:
        class DummyLed:
            def wifi_connecting(self): pass
            def mqtt_connecting(self): pass
            def set_state(self, r, g, b): pass
            def off(self): pass
        led = DummyLed()
        print("No status LED file found. Proceeding without LED.")

def connect():
    """
    Connects to the best available WiFi network from secrets.py.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    mac = ubinascii.hexlify(wlan.config("mac")).decode()

    for creds in WIFI_CREDENTIALS:
        wlan.disconnect()
        time.sleep(1)
        ssid = creds.get("ssid")
        password = creds.get("password")

        print(f"Connecting to SSID: {ssid}...")
        wlan.connect(ssid, password)

        # Wait max 10 seconds for connection
        max_wait = 10
        while max_wait > 0:
            led.wifi_connecting()
            if wlan.isconnected():
                break
            max_wait -= 1
            time.sleep(1)

        if wlan.isconnected():
            print("-" * 30)
            print("WiFi connected successfully!")
            print(f"IP:   {wlan.ifconfig()[0]}")
            print(f"MAC:  {mac.upper()}")
            print("-" * 30)
            led.set_state(0, 0, 0) # Turn LED off
            return True

    print("WiFi connection failed for all credentials.")
    return False