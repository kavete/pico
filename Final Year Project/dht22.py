from machine import Pin
import dht
import time


dht_pin = Pin(15)
dht_sensor = dht.DHT22(dht_pin)

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
    
