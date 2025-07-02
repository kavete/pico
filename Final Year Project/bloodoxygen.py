from machine import I2C, Pin
from max30102 import MAX30102
import time

# I2C setup
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)
sensor = MAX30102(i2c)
sensor.setup_sensor()

# Buffers for IR and RED values
ir_buffer = []
red_buffer = []

# SpO₂ estimation using AC/DC ratio
def calculate_spo2(ir_vals, red_vals):
    if len(ir_vals) < 20 or len(red_vals) < 20:
        return None

    ir_samples = ir_vals[-20:]
    red_samples = red_vals[-20:]

    ir_dc = sum(ir_samples) / len(ir_samples)
    red_dc = sum(red_samples) / len(red_samples)

    ir_ac = max(ir_samples) - min(ir_samples)
    red_ac = max(red_samples) - min(red_samples)

    if ir_ac == 0 or ir_dc == 0 or red_dc == 0:
        return None

    ratio = (red_ac / red_dc) / (ir_ac / ir_dc)
    spo2 = 110 - 25 * ratio
    spo2 = max(0, min(100, spo2))  # clamp to valid range
    return round(spo2, 1)

print("🩸 SpO₂ estimation starting (no smoothing)...")

while True:
    sensor.check()
    if sensor.available():
        red = sensor.pop_red_from_storage()
        ir = sensor.pop_ir_from_storage()

        ir_buffer.append(ir)
        red_buffer.append(red)

        # Keep the buffer size reasonable
        if len(ir_buffer) > 100:
            ir_buffer.pop(0)
            red_buffer.pop(0)

        # Estimate and print SpO₂ every 20+ samples
        if len(ir_buffer) >= 20:
            spo2 = calculate_spo2(ir_buffer, red_buffer)
            if spo2 is not None:
                print("🩸 SpO₂:", spo2, "%")
            else:
                print("⏳ Estimating SpO₂...")

    time.sleep(0.1)
