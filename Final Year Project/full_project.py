from machine import Pin, ADC, I2C
import dht
import time
from max30102 import MAX30102
import network
from umqtt.simple import MQTTClient
from ssd1306 import SSD1306_I2C

# -- Wi-Fi Credentials --
SSID = secrets.SSID
PASSWORD = secrets.PASSWORD

WIDTH  = 128                                            # oled display width
HEIGHT = 64                                            # oled display height

# -- MQTT Broker Setup --
MQTT_SERVER = secrets.MQTT_IP
CLIENT_ID = "pico_ward_all_sensors"
TOPIC_TEMP_DHT = b"ward/temperature_dht"
TOPIC_HUMID = b"ward/humidity"
TOPIC_SPO2 = b"ward/spo2"
TOPIC_HEART_RATE = b"ward/heart_rate"
TOPIC_SOUND = b"ward/sound"
TOPIC_LIGHT = b"ward/light"
TOPIC_TEMP_LM35 = b"ward/temperature_lm35"

# -- DHT22 (Temperature and Humidity) Setup --
dht_pin = Pin(15)
dht_sensor = dht.DHT22(dht_pin)

# -- MAX30102 (Heart Rate and SpO2) Setup --
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)
hr_sensor = MAX30102(i2c)
hr_sensor.setup_sensor()

# Buffers and variables for heart rate and SpO2
ir_buffer = []
red_buffer = []
time_buffer = []
min_interval = 520  # Minimum time (ms) between peaks for heart rate
last_peak_time = 0
bpm_list = []
spo2_list = []

# -- KY-038 (Sound Sensor) Setup --
sound_analog_pin = ADC(Pin(28))
sound_digital_pin = Pin(2, Pin.IN)
max_decibels = 100

# -- LDR (Light Sensor) Setup --
R_fixed = 470
Vcc = 5
ldr_adc = ADC(Pin(27))

# -- LM35 (Temperature Sensor) Setup --
lm35_adc = ADC(Pin(26))

# -- Connect to Wi-Fi --
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    print("Connecting to Wi-Fi...")
    time.sleep(1)

print("Wi-Fi connected:", wlan.ifconfig())

# -- Connect to MQTT broker --
client = MQTTClient(CLIENT_ID, MQTT_SERVER)
client.connect()
print("Connected to MQTT broker at", MQTT_SERVER)

# -- Timing control for less frequent sensors --
last_sensor_read_time = 0

# --- Sensor Reading Functions ---

def read_dht22():
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temperature, humidity
    except Exception as e:
        print(f"Error reading from DHT22: {e}")
        return None, None

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
    spo2 = max(0, min(100, spo2))
    
    return round(spo2, 1)

def read_ky038():
    analog_value = sound_analog_pin.read_u16()
    digital_value = sound_digital_pin.value()
    decibels = analog_value * max_decibels / 65535
    return decibels, digital_value

def read_ldr():
    ldr_raw = ldr_adc.read_u16()
    vout = (ldr_raw / 65535) * Vcc
    lux = vout * (1200 / 5)
    return lux

def read_lm35_temp():
    raw_value = lm35_adc.read_u16()
    voltage = (raw_value / 65535) * 3.3
    temperature_c = voltage * 100
    return temperature_c

# --- Main Loop ---
print("Starting integrated sensor monitoring...")

while True:
    # -- High-frequency task: Heart Rate and SpO2 --
    hr_sensor.check()
    
    if hr_sensor.available():
        red = hr_sensor.pop_red_from_storage()
        ir = hr_sensor.pop_ir_from_storage()
        current_time_hr = time.ticks_ms()
        
        ir_buffer.append(ir)
        red_buffer.append(red)
        time_buffer.append(current_time_hr)
        
        if len(ir_buffer) > 100:
            ir_buffer.pop(0)
            red_buffer.pop(0)
            time_buffer.pop(0)
            
        if len(ir_buffer) >= 20:
            mid = len(ir_buffer) - 10
            if (mid > 0 and mid < len(ir_buffer) - 1 and
                ir_buffer[mid] > ir_buffer[mid - 1] and
                ir_buffer[mid] > ir_buffer[mid + 1] and
                ir_buffer[mid] > 10000):
                
                delta = time.ticks_diff(current_time_hr, last_peak_time)
                if delta > min_interval:
                    bpm = 60000 / delta
                    bpm_list.append(bpm)
                    last_peak_time = current_time_hr
                    
                    spo2 = calculate_spo2(ir_buffer, red_buffer)
                    if spo2 is not None:
                        spo2_list.append(spo2)
                    
                    if len(bpm_list) >= 5:
                        avg_bpm = sum(bpm_list) / len(bpm_list)
                        if len(spo2_list) > 0:
                            avg_spo2 = sum(spo2_list) / len(spo2_list)
                            print(f"Heart Rate: {int(avg_bpm)} BPM | SpO2: {round(avg_spo2, 1)}%")
                            client.publish(TOPIC_HEART_RATE, str(int(avg_bpm)))
                            client.publish(TOPIC_SPO2, str(round(avg_spo2, 1)))
                            spo2_list = []
                        else:
                            print(f"Heart Rate: {int(avg_bpm)} BPM | SpO2: Calculating...")
                            client.publish(TOPIC_HEART_RATE, str(int(avg_bpm)))
                        bpm_list = []

    # -- Low-frequency tasks: Other sensors (run every 2 seconds) --
    current_time_sensors = time.ticks_ms()
    if time.ticks_diff(current_time_sensors, last_sensor_read_time) > 2000:
        last_sensor_read_time = current_time_sensors
        
        print("\n--- Sensor Snapshot ---")
        
        # Read DHT22
        dht_temp, dht_humidity = read_dht22()
        if dht_temp is not None:
            print(f"DHT22 Temp: {dht_temp:.1f}°C | Humidity: {dht_humidity:.1f}%")
            client.publish(TOPIC_TEMP_DHT, str(dht_temp))
            client.publish(TOPIC_HUMID, str(dht_humidity))
            
        # Read LM35 Temperature
        lm35_temp = read_lm35_temp()
        print(f"LM35 Temp: {lm35_temp:.2f}°C")
        client.publish(TOPIC_TEMP_LM35, str(lm35_temp))
        
        # Read LDR Light Level
        lux = read_ldr()
        print(f"Light Level: {lux:.2f} Lux")
        client.publish(TOPIC_LIGHT, str(lux))
        
        # Read KY-038 Sound Level
        decibels, digital_sound = read_ky038()
        print(f"Sound Level: {decibels:.2f} dB | Digital: {digital_sound}")
        client.publish(TOPIC_SOUND, str(decibels))
        print("-----------------------\n")
        print("Published sensor data to MQTT.")

    time.sleep(0.01) # Keep the loop responsive for the heart rate sensor
