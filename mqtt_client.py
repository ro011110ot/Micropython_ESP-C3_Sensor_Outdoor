# mqtt_client.py
import json
import secrets
import time
from umqtt.simple import MQTTClient


class MQTT:
    """
    Universal MQTT client for both Dashboard (Receiver) and Sensors (Sender).
    Supports SSL, Retained Messages, and dynamic Callbacks.
    English comments and docstrings.
    """

    def __init__(self):
        self.broker = secrets.MQTT_BROKER
        self.port = secrets.MQTT_PORT
        self.user = secrets.MQTT_USER
        self.password = secrets.MQTT_PASS
        self.device_id = secrets.MQTT_CLIENT_ID
        self.use_ssl = secrets.MQTT_USE_SSL

        self.is_connected = False
        self.callbacks = []

        # Initialize the underlying MicroPython MQTT client
        self.client = MQTTClient(
            client_id=self.device_id,
            server=self.broker,
            port=self.port,
            user=self.user,
            password=self.password,
            keepalive=60,
            ssl=self.use_ssl
        )
        self.client.set_callback(self._internal_callback)

    def _internal_callback(self, topic, msg):
        """Routes incoming messages to all registered listeners."""
        try:
            t = topic.decode()
            m = msg.decode()

            # Print for debugging on the Dashboard
            print(f"MQTT RECEIVE: [{t}] -> {m}")

            for cb in self.callbacks:
                try:
                    cb(t, m)
                except Exception as e:
                    print(f"Callback error: {e}")
        except Exception as e:
            print(f"MQTT Decode error: {e}")

    def set_callback(self, cb):
        """Registers a function to handle incoming messages."""
        if cb not in self.callbacks:
            self.callbacks.append(cb)

    def connect(self):
        """Connects to the broker. Returns True if successful."""
        print(f"Connecting to MQTT via {'SSL' if self.use_ssl else 'TCP'}...")
        try:
            # Set Last Will and Testament (LWT)
            lwt_topic = f"status/{self.device_id}"
            self.client.set_last_will(lwt_topic, "offline", retain=True)

            self.client.connect()

            # Publish online status
            self.client.publish(lwt_topic, "online", retain=True)

            self.is_connected = True
            print("MQTT connected successfully.")
            return True
        except Exception as e:
            print(f"MQTT Connection failed: {e}")
            self.is_connected = False
            return False

    def subscribe(self, topic):
        """Subscribes to a topic. Used by the Dashboard."""
        if self.is_connected:
            try:
                self.client.subscribe(topic)
                print(f"Subscribed: {topic}")
                return True
            except Exception as e:
                print(f"Subscription failed: {e}")
                self.is_connected = False
                return False
        return False

    def publish(self, data, topic="Sensors", retain=False):
        """
        Publishes data as JSON.
        Supports 'retain' for sensor values to be stored by the broker.
        """
        if not self.is_connected:
            return False
        try:
            # Convert dict/list to JSON string
            payload = json.dumps(data)
            self.client.publish(topic, payload, retain=retain)
            return True
        except Exception as e:
            print(f"Publish failed: {e}")
            return False

    def check_msg(self):
        """Checks for new messages. Vital for the Dashboard loop."""
        if self.is_connected:
            try:
                self.client.check_msg()
            except Exception as e:
                print(f"MQTT check_msg error: {e}")
                self.is_connected = False
                raise e  # Forward error to main loop for reset handling