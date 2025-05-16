import network
import time
import dht
from machine import Pin
from umqtt.simple import MQTTClient
import secrets

# Adafruit IO credentials
AIO_USER = secrets.AIO_USER
AIO_KEY = secrets.AIO_KEY
TEMP_FEED = secrets.TEMP_FEED
HUMIDITY_FEED = secrets.HUMIDITY_FEED

# Wi-Fi credentials
SSID = secrets.SSID
PASSWORD = secrets.PASSWORD

# Connect Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    time.sleep(1)

print("Wi-Fi connected")

# Wait before starting sensor
time.sleep(2)

# Set up DHT22 (connected to GPIO15)
dht_sensor = dht.DHT22(Pin(15))

# Set up MQTT
mqtt_server = "io.adafruit.com"
client = MQTTClient("pico", mqtt_server, user=AIO_USER, password=AIO_KEY)
client.connect()

# Main loop
while True:
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        client.publish(TEMP_FEED, str(temp))
        client.publish(HUMIDITY_FEED, str(humidity))
        print("Sent → Temp:", temp, "°C | Humidity:", humidity, "%")
    except Exception as e:
        print("Sensor error:", e)

    time.sleep(5)
