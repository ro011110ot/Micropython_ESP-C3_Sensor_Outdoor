# mqtt_client.py
import json
import machine
import secrets
from umqtt.simple import MQTTClient


class MQTT:
    """
    MQTT client with SSL support, Last Will (LWT), and publishing capabilities.
    Unified version for all sensor nodes.
    """

    def __init__(self):
        # Load credentials from secrets.py
        self.broker = secrets.MQTT_BROKER
        self.port = secrets.MQTT_PORT
        self.user = secrets.MQTT_USER
        self.password = secrets.MQTT_PASS
        self.device_id = secrets.MQTT_CLIENT_ID
        self.use_ssl = secrets.MQTT_USE_SSL

        self.is_connected = False
        self.callbacks = []

        # Initialize the MQTT client
        self.client = MQTTClient(
            client_id=self.device_id,
            server=self.broker,
            port=self.port,
            user=self.user,
            password=self.password,
            keepalive=60,
            ssl=self.use_ssl
        )

    def connect(self):
        """Connect to the broker with Last Will and Testament."""
        print(f"Connecting to MQTT via {'SSL' if self.use_ssl else 'TCP'}...")
        try:
            lwt_topic = f"status/{self.device_id}"
            self.client.set_last_will(lwt_topic, "offline", retain=True)
            self.client.connect()
            self.client.publish(lwt_topic, "online", retain=True)
            self.is_connected = True
            print("MQTT connected successfully.")
            return True
        except Exception as e:
            print(f"MQTT Connection failed: {e}")
            self.is_connected = False
            return False

    def publish(self, data, topic="Sensors"):
        """
        Publishes data as a JSON string to the specified topic.
        """
        if not self.is_connected:
            print("Cannot publish: Not connected to MQTT.")
            return False

        try:
            payload = json.dumps(data)
            self.client.publish(topic, payload)
            return True
        except Exception as e:
            print(f"Publish failed: {e}")
            return False

    def check_msg(self):
        """Checks for incoming messages."""
        if self.is_connected:
            try:
                self.client.check_msg()
            except:
                self.is_connected = False