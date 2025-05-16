from machine import Pin, I2C
import dht
import time
from ssd1306 import SSD1306_I2C

dht_pin = Pin(15)
dht_sensor = dht.DHT22(dht_pin)

WIDTH  = 128                                            # oled display width
HEIGHT = 64                                            # oled display height

i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=200000)       # Init I2C using pins GP8 & GP9 (default I2C0 pins)
print("I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
print("I2C Configuration: "+str(i2c))                   # Display I2C config


oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

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
    
    
    oled.fill(0)

    # Add some text
    string_temp = str(temperature)
    oled.text("Temp:" + string_temp,4,8)
    oled.text("Humidity:" + str(humidity),5,18)

    # Finally update the oled display so the image & text is displayed
    oled.show()
    time.sleep(1)
    
    


