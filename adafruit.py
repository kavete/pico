# Import required libraries

import network
import time
import dht
from machine import Pin
from umqtt.simple import MQTTClient
import secrets

# Adafruit IO credentials
AIO_USER = secrets.AIO_USER
AIO_KEY = secrets.AIO_KEY
WARD_TEMP_FEED = secrets.WARD_TEMP_FEED
WARD_HUMIDITY_FEED = secrets.WARD_HUMIDITY_FEED

# Wi-Fi credentials
SSID = secrets.SSID
PASSWORD = secrets.PASSWORD

print(SSID, PASSWORD)
# Connect Wi-Fi with timeout
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
print("Connecting to Wi-Fi...")

max_wait = 20  # seconds
time_waited = 0
while not wlan.isconnected() and time_waited < max_wait:
    print(f"Waiting for connection... {time_waited+1}s")
    time.sleep(1)
    time_waited += 1

if wlan.isconnected():
    print("Wi-Fi connected. IP:", wlan.ifconfig()[0])
else:
    print("Failed to connect to Wi-Fi after", max_wait, "seconds.")
    raise RuntimeError("Wi-Fi connection failed")

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
        
        client.publish(WARD_TEMP_FEED, str(temp))
        client.publish(WARD_HUMIDITY_FEED, str(humidity))
        print("Sent → Temp:", temp, "°C | Humidity:", humidity, "%")
    except Exception as e:
        print("Sensor error:", e)

    time.sleep(5)
