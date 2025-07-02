from machine import I2S, Pin
import uarray as array  # Use 'array' if uarray is unavailable

# I2S config
i2s = I2S(
    I2S.NUM0,                      # I²S peripheral number (NUM0 or NUM1)
    sck=Pin(32),                   # BCLK
    ws=Pin(25),                    # LRCK/WS
    sd=Pin(33),                    # Serial data in (from INMP441)
    mode=I2S.RX,                   # Receive mode
    bits=16,                       # Data resolution (16-bit)
    format=I2S.MONO,               # Mono input (L/R pin decides channel)
    rate=16000,                    # Sample rate (e.g., 16 kHz)
    ibuf=4000                      # Internal buffer size
)

# Buffer to hold audio samples
audio_samples = array.array('H', [0] * 1024)  # 'H' for 16-bit unsigned samples

print("Reading audio... Press Ctrl+C to stop.")
try:
    while True:
        num_read = i2s.readinto(audio_samples)
        if num_read:
            # Do something with audio_samples
            print("Read", num_read, "bytes")
except KeyboardInterrupt:
    print("Stopped.")
finally:
    i2s.deinit()
