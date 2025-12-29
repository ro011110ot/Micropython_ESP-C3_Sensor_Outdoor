# ESP32-C3 Outdoor Sensor Station

This project is part of a MicroPython-based sensor ecosystem. This specific node is designed for outdoor temperature monitoring using an **ESP32-C3** and **DS18B20** waterproof sensors.



## 🚀 Features
* **MQTT Telemetry**: Publishes temperature data in JSON format to a central broker.
* **Auto-Recovery**: Hardware Watchdog and automatic WiFi/MQTT reconnection logic.
* **Accurate Timing**: RTC synchronization via NTP with automatic CET/CEST daylight saving adjustment.
* **Energy Efficient**: Optimized loop for long-term environment monitoring.

## 🛠 Hardware
* **Microcontroller**: ESP32-C3
* **Sensor**: DS18B20 (OneWire)
* **Connectivity**: WiFi (2.4GHz)

## 📂 Data Format
Data is published to the `Sensors` topic as follows:
```json
{
  "id": "Sensor_DS18B20_Aussen",
  "value": 4.52,
  "unit": "°C"
}