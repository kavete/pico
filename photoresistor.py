from machine import Pin, ADC
import time

res = ADC(Pin(28))
led = Pin(15, Pin.OUT)
conversion_factor = 5/ 65535

while True:
    res_value = res.read_u16()
    print(res_value)
    print(res_value*conversion_factor)
    if res_value  > 50000:
        led.value(1)
    else:
        led.value(0)
        
    time.sleep(1)