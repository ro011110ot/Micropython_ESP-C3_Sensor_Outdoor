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

    # Read and format MAC address
    mac = ubinascii.hexlify(wlan.config("mac")).decode()

    for creds in WIFI_CREDENTIALS:
        wlan.disconnect()
        time.sleep(1)

        ssid = creds.get("ssid")
        password = creds.get("password")

        print(f"Connecting to {ssid}...")
        wlan.connect(ssid, password)

        # Wait for connection (max 10 seconds)
        max_wait = 10
        while max_wait > 0:
            led.wifi_connecting()
            if wlan.isconnected():
                break
            max_wait -= 1
            time.sleep(1)

        if wlan.isconnected():
            config = wlan.ifconfig()
            ip_address = config[0]

            print("-" * 30)
            print("WiFi connected successfully!")
            print(f"SSID: {ssid}")
            print(f"IP:   {ip_address}")
            print(f"MAC:  {mac.upper()}")
            print("-" * 30)

            # Set LED to off
            led.set_state(0, 0, 0)
            return True 

    if not wlan.isconnected():
        led.set_state(255, 0, 0) # Red for error
        print(f"Error: Could not connect to any network. MAC: {mac.upper()}")
        raise RuntimeError("Network connection failed")
    return False