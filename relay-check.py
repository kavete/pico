from machine import Pin
import time

relay = Pin(16, Pin.OUT)

while True:
    relay.value(1)
    time.sleep(1)
    relay.value(0)
    time.sleep(1)