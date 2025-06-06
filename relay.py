from machine import Pin
import time

led = Pin(16, Pin.OUT)
PIR = Pin(15, Pin.IN)
while(True):
    if PIR.value() == 1:
        led.value(1)
        print("Motion Detected")
        #bulb.value(1)
        #time.sleep(3)
    elif PIR.value() == 0:
        led.value(0)
        print("No Motion")
        #bulb.value(0)
    print(PIR.value())
    time.sleep(1)
    

