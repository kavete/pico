from machine import ADC, Pin
import time

# Configure the ADC pin (use correct GPIO number; here GPIO26 for Pico or 36 for ESP32)
adc = ADC(Pin(26))  # For Raspberry Pi Pico, use GP26 (ADC0)

# If using ESP32, use something like:
# adc = ADC(Pin(36))
# adc.atten(ADC.ATTN_11DB)  # For ESP32 to handle full voltage range

def read_temperature():
    raw_value = adc.read_u16()  # 16-bit value (0 - 65535)
    voltage = (raw_value / 65535) * 3.3  # Convert ADC value to voltage
    temperature_c = voltage * 100  # LM35 outputs 10mV per °C
    return temperature_c

while True:
    temp = read_temperature()
    print("Temperature: {:.2f} °C".format(temp))
    time.sleep(1)
