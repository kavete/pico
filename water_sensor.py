from machine import Pin, ADC
import time

level_sensor = ADC(Pin(28))
solenoid_valve = Pin(15, Pin.OUT)

while True:
    level = level_sensor.read_u16()
    print(level)
    time.sleep(1)

    if level > 20000:
       print("Water level is low")
       solenoid_valve.value(0)
    else:
        
        print("Water level is high")
        solenoid_valve.value(1)
        
        
    print(solenoid_valve.value())
