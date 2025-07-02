import network
import time
import dht
from machine import Pin
from umqtt.simple import MQTTClient

# Wi-Fi credentials
SSID = secrets.SSID
PASSWORD = secrets.PASSWORD

# MQTT broker IP 
MQTT_SERVER = secrets.IP
CLIENT_ID = "pico_ward"
TOPIC_TEMP = b"ward/temp"
TOPIC_HUMID = b"ward/humidity"


# DHT22 sensor on GPIO 15
sensor = dht.DHT22(Pin(15))

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    print("Connecting to Wi-Fi...")
    time.sleep(1)

print("Wi-Fi connected:", wlan.ifconfig())

# Connect to MQTT broker
client = MQTTClient(CLIENT_ID, MQTT_SERVER)
client.connect()
print("Connected to MQTT broker at", MQTT_SERVER)

# Main loop
while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        humidity = sensor.humidity()
        
        print("Temp:", temp, "°C | Humidity:", humidity, "%")
        
        client.publish(TOPIC_TEMP, str(temp))
        client.publish(TOPIC_HUMID, str(humidity))
        print("Published to MQTT.")

    except Exception as e:
        print("Error:", e)
    
    time.sleep(1)  # wait 5 seconds

