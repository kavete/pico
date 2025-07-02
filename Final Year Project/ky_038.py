from machine import Pin, ADC
import time

# Initialize pins
analog_pin = ADC(Pin(28))  # ADC2 on Pin 28 for analog output
digital_pin = Pin(2, Pin.IN)  # GPIO 2 for digital output (adjust as needed)
max_decibels = 100
def read_ky038():
    # Read analog value (0-65535)
    analog_value = analog_pin.read_u16()
    # Convert to voltage (assuming 3.3V reference)
    voltage = analog_value * 3.3 / 65535
    # Read digital value (0 or 1)
    digital_value = digital_pin.value()

    decibels = analog_value * max_decibels/ 65535
    return analog_value, voltage, digital_value, decibels

# Main loop
while True:
    analog_val, voltage_val, digital_val, decibels = read_ky038()
    print(f"Analog: {analog_val}, Voltage: {voltage_val:.2f}V, Digital: {digital_val}")
    print(f"Decibels: {decibels:.2f} dB")
    time.sleep(0.1)  # Delay 1s between readings
