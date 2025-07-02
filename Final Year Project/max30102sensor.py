from machine import I2C, Pin
from max30102 import MAX30102
import time

# I2C Setup
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)
sensor = MAX30102(i2c)
sensor.setup_sensor()

# Variables
ir_buffer = []
time_buffer = []
min_interval = 520  # Minimum time (ms) between peaks
last_peak_time = 0
bpm_list = []

print("Starting heart rate detection...")

while True:
    sensor.check()
    if sensor.available():
        sensor.pop_red_from_storage()  # Read and discard RED if not needed
        ir = sensor.pop_ir_from_storage()

        current_time = time.ticks_ms()
        ir_buffer.append(ir)
        time_buffer.append(current_time)

        if len(ir_buffer) > 20:
            ir_buffer.pop(0)
            time_buffer.pop(0)

        # Simple peak detection
        if len(ir_buffer) == 20:
            mid = 10
            if (ir_buffer[mid] > ir_buffer[mid - 1] and
                ir_buffer[mid] > ir_buffer[mid + 1] and
                ir_buffer[mid] > 10000):  # Threshold can be tuned
                delta = time.ticks_diff(current_time, last_peak_time)
                if delta > min_interval:
                    bpm = 60000 / delta
                    bpm_list.append(bpm)
                    last_peak_time = current_time

                    if len(bpm_list) >= 5:
                        avg_bpm = sum(bpm_list) / len(bpm_list)
                        print("Average BPM:", int(avg_bpm))
                        bpm_list = []

    time.sleep(0.01)
