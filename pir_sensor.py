from machine import Pin
import time

PIR = Pin(15, Pin.IN)
led = Pin(16, Pin.OUT)

while(True):
    if PIR.value() == 1:
        led.value(1)
        print("Motion Detected")
        #time.sleep(3)
    elif PIR.value() == 0:
        led.value(0)
        print("No Motion")
    print(PIR.value())
    time.sleep(1)
    