# mqtt_client.py
import json
import machine
import secrets
from umqtt.simple import MQTTClient


class MQTT:
    """
    Unified MQTT client for Dashboard (S3) and Sensor Nodes (C3/Standard).
    Supports SSL, Last Will, Publishing, and Multi-Callback Subscriptions.
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
        self.vps_data = None  # Buffer for VPS metrics (Dashboard specific)
        self.callbacks = []  # List for registered listeners (e.g., SensorScreen)

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

        # Set the internal callback handler
        self.client.set_callback(self._internal_callback)

    def _internal_callback(self, topic, msg):
        """
        Internal dispatcher:
        1. Updates VPS data buffer.
        2. Forwards messages to all registered screen callbacks.
        """
        topic_str = topic.decode()

        # Handle VPS data (Dashboard use-case)
        if topic_str == "vps/monitor":
            try:
                self.vps_data = json.loads(msg)
            except:
                pass

        # Forward to external listeners (e.g., your Sensor Screen)
        for cb in self.callbacks:
            try:
                cb(topic, msg)
            except Exception as e:
                print(f"Callback error: {e}")

    def set_callback(self, cb):
        """Registers a new listener function for incoming messages."""
        if cb not in self.callbacks:
            self.callbacks.append(cb)

    def connect(self, topics=None):
        """
        Connects to the broker with Last Will and Testament.
        'topics' can be a list of strings to subscribe to (e.g., ["Sensors", "vps/monitor"]).
        """
        print(f"Connecting to MQTT via {'SSL' if self.use_ssl else 'TCP'}...")
        try:
            lwt_topic = f"status/{self.device_id}"
            self.client.set_last_will(lwt_topic, "offline", retain=True)
            self.client.connect()
            self.client.publish(lwt_topic, "online", retain=True)

            # Subscriptions (Mainly for the Dashboard)
            if topics:
                for t in topics:
                    self.client.subscribe(t)
                    print(f"Subscribed to topic: {t}")

            self.is_connected = True
            print("MQTT connected successfully.")
            return True
        except Exception as e:
            print(f"MQTT Connection failed: {e}")
            self.is_connected = False
            return False

    def publish(self, data, topic="Sensors"):
        """
        Publishes data as a JSON string. Used by Sensor Nodes.
        """
        if not self.is_connected:
            return False

        try:
            payload = json.dumps(data)
            self.client.publish(topic, payload)
            return True
        except Exception as e:
            print(f"Publish failed: {e}")
            return False

    def check_msg(self):
        """Checks for new messages. Must be called regularly in the main loop."""
        if self.is_connected:
            try:
                self.client.check_msg()
            except:
                self.is_connected = False

    def subscribe(self, topic):
        """Manual subscription helper."""
        if self.is_connected:
            try:
                self.client.subscribe(topic)
                print(f"Subscribed to: {topic}")
            except:
                self.is_connected = False