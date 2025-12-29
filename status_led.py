# status_led.py
from machine import Pin
import time

class StatusLed:
    """
    Handles a simple status LED on a specific GPIO pin.
    Provides methods for blinking and state indication.
    """
    def __init__(self, pin_number=2):
        self.pin = Pin(pin_number, Pin.OUT)
        self.off()

    def on(self):
        """Turn the LED on."""
        self.pin.value(1)

    def off(self):
        """Turn the LED off."""
        self.pin.value(0)

    def set_state(self, r, g, b):
        """
        Interprets RGB values for a simple (single-color) LED.
        The LED turns on if any color component is greater than 0.
        """
        if (r + g + b) > 0:
            self.on()
        else:
            self.off()

    def blink(self, duration=0.2, num_blinks=1):
        """Blinks the LED for a specific duration and count."""
        for _ in range(num_blinks):
            self.on()
            time.sleep(duration)
            self.off()
            time.sleep(duration)

    def wifi_connecting(self):
        """Short rapid blinks to indicate WiFi connection attempt."""
        self.blink(duration=0.1, num_blinks=3)

    def mqtt_connecting(self):
        """Longer blinks to indicate MQTT connection attempt."""
        self.blink(duration=0.4, num_blinks=2)