from machine import Pin, ADC
import time

level_sensor = ADC(Pin(28))
solenoid_valve = Pin(16, Pin.OUT)

while True:
    level = level_sensor.read_u16()
    print(level)
    time.sleep(1)


    if level > 30000:
        print("Water level is high")
        solenoid_valve.value(1)
    else:
        print("Water level is low")
        solenoid_valve.value(0)
