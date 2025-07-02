# Import required libraries
import network
import time
import dht
from machine import Pin, ADC, I2C
from umqtt.simple import MQTTClient
import secrets
from max30102 import MAX30102

# Adafruit IO credentials
AIO_USER = secrets.AIO_USER
AIO_KEY = secrets.AIO_KEY
WARD_TEMP_FEED = secrets.WARD_TEMP_FEED
WARD_HUMIDITY_FEED = secrets.WARD_HUMIDITY_FEED
PATIENT_TEMPERATURE_FEED = secrets.PATIENT_TEMPERATURE_FEED
LIGHT_INTENSITY_FEED = secrets.LIGHT_INTENSITY_FEED
BLOOD_OXYGEN_FEED = secrets.BLOOD_OXYGEN_FEED
HEART_RATE_FEED = secrets.HEART_RATE_FEED

# Wi-Fi credentials
SSID = secrets.SSID
PASSWORD = secrets.PASSWORD

print(SSID, PASSWORD)

# Connect Wi-Fi with timeout
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
print("Connecting to Wi-Fi...")

max_wait = 20  # seconds
time_waited = 0
while not wlan.isconnected() and time_waited < max_wait:
    print(f"Waiting for connection... {time_waited+1}s")
    time.sleep(1)
    time_waited += 1

if wlan.isconnected():
    print("Wi-Fi connected. IP:", wlan.ifconfig()[0])
else:
    print("Failed to connect to Wi-Fi after", max_wait, "seconds.")
    raise RuntimeError("Wi-Fi connection failed")

# Wait before starting sensor
time.sleep(2)

# Set up sensors
dht_sensor = dht.DHT22(Pin(15))
max30102_sensor = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)
max_sensor = MAX30102(max30102_sensor)
max_sensor.setup_sensor()

lm35 = ADC(Pin(26))
R_fixed = 470  # Ohms
Vcc = 5
ldr = ADC(Pin(27))

# Buffers for IR and RED values
ir_buffer = []
red_buffer = []
time_buffer = []

# Heart rate detection variables
min_interval = 520  # Minimum time (ms) between peaks
last_peak_time = 0
bpm_list = []
spo2_list = []

# Initialize variables for heart rate and SpO2
avg_bpm = 0
avg_spo2 = 0

def read_temperature():
    raw_value = lm35.read_u16()  # 16-bit value (0 - 65535)
    voltage = (raw_value / 65535) * 3.3  # Convert ADC value to voltage
    temperature_c = voltage * 100  # LM35 outputs 10mV per °C
    return temperature_c

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

def process_max30102():
    global avg_bpm, avg_spo2, last_peak_time, bpm_list, spo2_list
    
    max_sensor.check()
    
    if max_sensor.available():
        red = max_sensor.pop_red_from_storage()
        ir = max_sensor.pop_ir_from_storage()
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
                    bpm_list.append(bmp)
                    last_peak_time = current_time
                    
                    # Collect SpO₂ for averaging
                    spo2 = calculate_spo2(ir_buffer, red_buffer)
                    if spo2 is not None:
                        spo2_list.append(spo2)
                    
                    if len(bpm_list) >= 5:
                        avg_bpm = sum(bpm_list) / len(bpm_list)
                        
                        # Calculate SpO₂ average if available
                        if len(spo2_list) > 0:
                            avg_spo2 = sum(spo2_list) / len(spo2_list)
                            print("Heart Rate:", int(avg_bpm), "BPM | SpO₂:", round(avg_spo2, 1), "%")
                            spo2_list = []
                        else:
                            print("Heart Rate:", int(avg_bpm), "BPM | SpO₂: Calculating...")
                        
                        bpm_list = []

# Set up MQTT with reconnection function
mqtt_server = "io.adafruit.com"
client = None

def connect_mqtt():
    global client
    try:
        client = MQTTClient("pico", mqtt_server, user=AIO_USER, password=AIO_KEY, keepalive=60)
        client.connect()
        print("MQTT connected successfully")
        return True
    except Exception as e:
        print("MQTT connection failed:", e)
        return False

def publish_with_retry(feed, value, max_retries=3):
    global client
    for attempt in range(max_retries):
        try:
            if client is None:
                if not connect_mqtt():
                    continue
            
            client.publish(feed, str(value))
            return True
            
        except Exception as e:
            print(f"Publish attempt {attempt + 1} failed:", e)
            client = None  # Reset client to force reconnection
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
    
    return False

# Initial MQTT connection
connect_mqtt()

# Main loop
while True:
    try:
        # Read DHT22 sensor
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        # Read patient temperature
        patient_temp = read_temperature()
        
        # Read light sensor
        ldr_raw = ldr.read_u16()
        vout = (ldr_raw / 65535) * Vcc
        lux = vout * (1200/5)
        
        print("Temperature: {:.2f} °C".format(patient_temp))
        print("Ward Temp:", temp, "°C | Ward Humidity:", humidity, "%")
        print("Estimated Lux: {:.2f}".format(lux))
        print("Voltage (Vout): {:.2f} V".format(vout))
        
        # Process MAX30102 sensor data
        process_max30102()
        
        # Publish to MQTT with retry mechanism
        publish_with_retry(WARD_TEMP_FEED, temp)
        publish_with_retry(WARD_HUMIDITY_FEED, humidity)
        publish_with_retry(PATIENT_TEMPERATURE_FEED, patient_temp)
        publish_with_retry(LIGHT_INTENSITY_FEED, lux)
        
        # Only publish heart rate and SpO2 if we have valid readings
        if avg_bpm > 0:
            publish_with_retry(HEART_RATE_FEED, int(avg_bpm))
        if avg_spo2 > 0:
            publish_with_retry(BLOOD_OXYGEN_FEED, round(avg_spo2, 1))
        
        print("Sent Ward Temp:", temp, "°C | Ward Humidity:", humidity, "%", "| Patient temp:", patient_temp, "°C")
        if avg_bpm > 0 and avg_spo2 > 0:
            print("Sent Light intensity:", lux, "lux | Heart rate:", int(avg_bpm), "| Blood Oxygen:", round(avg_spo2, 1), "%")
        else:
            print("Sent Light intensity:", lux, "lux | Heart rate: waiting... | Blood Oxygen: waiting...")
        
    except Exception as e:
        print("Sensor error:", e)

    time.sleep(5)