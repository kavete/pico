# Import required libraries

import network
import time
import dht
from machine import Pin,ADC
from umqtt.simple import MQTTClient
import secrets

# Adafruit IO credentials
AIO_USER = secrets.AIO_USER
AIO_KEY = secrets.AIO_KEY
WARD_TEMP_FEED = secrets.WARD_TEMP_FEED
WARD_HUMIDITY_FEED = secrets.WARD_HUMIDITY_FEED
PATIENT_TEMPERATURE_FEED = secrets.PATIENT_TEMPERATURE_FEED
LIGHT_INTENSITY_FEED = secrets.LIGHT_INTENSITY_FEED
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

lm35 = ADC(Pin(26))
R_fixed = 20000  # 20kΩ
Vcc = 5
ldr = ADC(Pin(27))

def read_temperature():
    raw_value = lm35.read_u16()  # 16-bit value (0 - 65535)
    voltage = (raw_value / 65535) * 3.3  # Convert ADC value to voltage
    temperature_c = voltage * 100  # LM35 outputs 10mV per °C
    return temperature_c

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
        patient_temp = read_temperature()
        ldr_raw = ldr.read_u16()
        vout = (ldr_raw / 65535) * Vcc
        lux = vout * (700/5)
        
        print("Temperature: {:.2f} °C".format(patient_temp))
        print(temp)
        print(humidity)
        print("Estimated Lux: {:.2f}".format(lux))
        print("Voltage (Vout): {:.2f} V".format(vout))
        
        
        
        client.publish(WARD_TEMP_FEED, str(temp))
        client.publish(WARD_HUMIDITY_FEED, str(humidity))
        client.publish(PATIENT_TEMPERATURE_FEED, str(patient_temp))
        client.publish(LIGHT_INTENSITY_FEED, str(lux))
        print("Sent → Temp:", temp, "°C | Humidity:", humidity, "%", "|", "Patient temp: ", patient_temp, "°C")
    except Exception as e:
        print("Sensor error:", e)

    time.sleep(5)

