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
time_buffer = []

# Heart rate detection variables
min_interval = 520  # Minimum time (ms) between peaks
last_peak_time = 0
bpm_list = []
spo2_list = []

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

print("Heart Rate & SpO2 Monitor Starting...")

while True:
    sensor.check()
    
    if sensor.available():
        red = sensor.pop_red_from_storage()
        ir = sensor.pop_ir_from_storage()
        current_time = time.ticks_ms()
        
        # Add to buffers
        ir_buffer.append(ir)
        red_buffer.append(red)
        time_buffer.append(current_time)
        
        # Keep buffer size reasonable
        if len(ir_buffer) > 100:
            ir_buffer.pop(0)
            red_buffer.pop(0)
            time_buffer.pop(0)
        
        # Heart rate detection (needs at least 20 samples)
        if len(ir_buffer) >= 20:
            mid = len(ir_buffer) - 10  # Use recent middle point
            
            # Peak detection
            if (mid > 0 and mid < len(ir_buffer) - 1 and
                ir_buffer[mid] > ir_buffer[mid - 1] and
                ir_buffer[mid] > ir_buffer[mid + 1] and
                ir_buffer[mid] > 10000):  # Threshold can be tuned
                
                delta = time.ticks_diff(current_time, last_peak_time)
                
                if delta > min_interval:
                    bpm = 60000 / delta
                    bpm_list.append(bpm)
                    last_peak_time = current_time
                    
                    # Collect SpO₂ for averaging
                    spo2 = calculate_spo2(ir_buffer, red_buffer)
                    if spo2 is not None:
                        spo2_list.append(spo2)
                    
                    if len(bpm_list) >= 5:
                        avg_bpm = sum(bpm_list) / len(bpm_list)
                        
                        # Display SpO₂ average if available
                        if len(spo2_list) > 0:
                            avg_spo2 = sum(spo2_list) / len(spo2_list)
                            print(" Heart Rate:", int(avg_bpm), "BPM |  SpO2:", round(avg_spo2, 1), "%")
                            spo2_list = []
                        else:
                            print("Heart Rate:", int(avg_bpm), "BPM | SpO2: Calculating...")
                        
                        bpm_list = []
    
    time.sleep(0.01)  # Balance between responsiveness and processing load