import ubinascii
import ujson
from machine import unique_id
from umqtt.simple import MQTTClient

# Neuer Import-Block in mqtt_client.py
try:
    from secrets import (
        MQTT_BROKER,
        MQTT_PORT,
        MQTT_USER,
        MQTT_PASS,
        MQTT_USE_SSL,
        MQTT_CLIENT_ID
    )
except ImportError:
    print("Error: Could not import 'secrets.py'")
    MQTT_BROKER = None
    MQTT_PORT = 0
    MQTT_USER = ""
    MQTT_PASS = ""
    MQTT_USE_SSL = False
    MQTT_CLIENT_ID = None


class MQTT:
    """
    A wrapper class for the umqtt.simple.MQTTClient.
    Handles connection, publishing, and disconnection.
    Formats and sends sensor data as JSON payloads.
    """

    def __init__(self):
        """
        Initializes the MQTT client.
        """
        if not MQTT_BROKER or not MQTT_PORT:
            raise ValueError(
                "MQTT_BROKER or MQTT_PORT is not defined or found in secrets.py"
            )

        self.client_id = MQTT_CLIENT_ID if MQTT_CLIENT_ID else ubinascii.hexlify(unique_id()).decode()
        self.broker = MQTT_BROKER
        self.port = MQTT_PORT
        self.user = MQTT_USER
        self.password = MQTT_PASS
        self.client = MQTTClient(
            self.client_id,
            self.broker,
            port=self.port,
            user=self.user,
            password=self.password,
            ssl=MQTT_USE_SSL,
            keepalive=60
        )
        self.is_connected = False

    def connect(self):
        """
        Connects to the MQTT broker.
        Returns True on success, False on failure.
        """
        print(f"Connecting to MQTT broker at {self.broker}:{self.port}...")
        try:
            self.client.connect()
            self.is_connected = True
            print("MQTT connected successfully.")
            return True
        except OSError as e:
            print(f"Failed to connect to MQTT broker: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """
        Disconnects from the MQTT broker.
        """
        if self.is_connected:
            print("Disconnecting from MQTT broker.")
            self.client.disconnect()
            self.is_connected = False

    def set_callback(self, callback):
        """
        Sets the callback function for incoming messages.
        """
        self.client.set_callback(callback)

    def subscribe(self, topic):
        """
        Subscribes to a topic.
        """
        if self.is_connected:
            print(f"Subscribing to topic: {topic}")
            self.client.subscribe(topic)

    def check_msg(self):
        """
        Checks for pending messages. Should be called periodically.
        """
        if self.is_connected:
            self.client.check_msg()


    def publish(self, sensor_data, topic="Sensors"):
        """
        Publiziert Daten direkt in ein Haupt-Topic.
        Standardmäßig 'Sensors', damit alle ESPs denselben Pfad nutzen.
        """
        if not self.is_connected:
            print("Nicht verbunden. Nachricht wird verworfen.")
            return

        payload = ujson.dumps(sensor_data).encode("utf-8")

        try:
            print(f"Sende an '{topic}': {payload}")
            self.client.publish(topic, payload)
        except Exception as e:
            print(f"Fehler beim Senden: {e}")
            self.is_connected = False