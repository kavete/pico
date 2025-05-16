from machine import Pin
import dht
import time
import urequests
import network
import secrets

dht_pin = Pin(15)
dht_sensor = dht.DHT22(dht_pin)
ssid= secrets.SSID
password = secrets.PASSWORD

def connect():
    wlan= network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while wlan.isconnected() == False:
        print("Connecting, Please wait")
        time.sleep(1)
    print("Connected! IP = ", wlan.ifconfig()[0])
    
try:
    connect()
   
except OSError as e:
    print("Error: Connection closed")
    

while True:
    try:
        dht_sensor.measure()
        
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        print("Temperature: ", temperature)
        print("Humidity: ", humidity)
        
    except Exception as e:
        print("Error reading from DHT22", str(e))
    time.sleep(5)
    
    url = "http://172.17.208.1:8000/receive/"
    data = {
    "temperature": temperature,
    "humidity": humidity,
    }

    response = urequests.post(url, json=data)
    print("Server response:", response.text)
    response.close()

