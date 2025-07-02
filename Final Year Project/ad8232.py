from machine import ADC, Pin
import time

# --- Pin Definitions ---
AD8232_SIG_PIN = 28  # Connect AD8232 SIG to Pico GP26 (ADC0)

# --- Initialize ADC Pin ---
adc = ADC(Pin(AD8232_SIG_PIN))

print("AD8232 ECG Sensor Reading (SIG pin)")
print("---------------------------------")

# --- Main Loop to Read Data ---
try:
    while True:
        # Read analog value from AD8232 SIG
        raw_value = adc.read_u16() # Reads a 16-bit unsigned integer (0-65535)

        # Convert raw value to voltage (Pico ADC is 3.3V max)
        # The AD8232's output is typically centered around VCC/2 (e.g., 3.3V/2 = 1.65V)
        # and swings positively and negatively around that. The Pico ADC only reads 0V to 3.3V.
        # This is fine, as the AD8232 usually biases its output appropriately for single-supply ADCs.
        voltage = raw_value * (3.3 / 65535)

        print(f"Raw ADC: {raw_value}, Voltage: {voltage:.4f}V")
            
        time.sleep(0.005) # Small delay for continuous reading

except KeyboardInterrupt:
    print("\nRecording stopped.")