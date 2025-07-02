from machine import Pin, PWM
import time

# Define the pin the buzzer is connected to
BUZZER_PIN = 13

# Create a PWM object for the buzzer pin
# A passive buzzer needs a varying frequency, which PWM provides
buzzer = PWM(Pin(BUZZER_PIN))

# --- Function to play a single tone ---
def play_tone(frequency, duration_ms):
    """
    Plays a single tone on the buzzer.
    frequency: The frequency of the tone in Hz (e.g., 500, 1000).
    duration_ms: The duration of the tone in milliseconds.
    """
    if frequency > 0:
        buzzer.freq(frequency)  # Set the frequency
        buzzer.duty_u16(32768)  # Set duty cycle to 50% (half of 65535 for 16-bit PWM)
    else:
        buzzer.duty_u16(0)      # Turn off the sound for a "rest"
    time.sleep_ms(duration_ms)
    buzzer.duty_u16(0)          # Turn off the sound after the duration

# --- Main demonstration ---
try:
    print("Testing passive buzzer...")

    # Play a simple high-pitched tone
    print("Playing a 1000 Hz tone for 500 ms...")
    play_tone(1000, 500)
    time.sleep(0.2) # Short pause

    # Play a lower-pitched tone
    print("Playing a 500 Hz tone for 300 ms...")
    play_tone(500, 300)
    time.sleep(0.2) # Short pause

    # Play a simple melody (example: "Twinkle Twinkle Little Star" opening)
    # Define notes and their approximate frequencies (you can refine these)
    NOTE_C4 = 262
    NOTE_D4 = 294
    NOTE_E4 = 330
    NOTE_F4 = 349
    NOTE_G4 = 392
    NOTE_A4 = 440
    NOTE_B4 = 494
    NOTE_C5 = 523

    print("Playing a short melody...")
    melody = [
        (NOTE_C4, 200), (NOTE_C4, 200), (NOTE_G4, 200), (NOTE_G4, 200),
        (NOTE_A4, 200), (NOTE_A4, 200), (NOTE_G4, 400),
        (NOTE_F4, 200), (NOTE_F4, 200), (NOTE_E4, 200), (NOTE_E4, 200),
        (NOTE_D4, 200), (NOTE_D4, 200), (NOTE_C4, 400)
    ]

    for note, duration in melody:
        play_tone(note, duration)
        time.sleep_ms(50) # Small pause between notes for clarity

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    # Always de-initialize the PWM peripheral to free up resources
    buzzer.deinit()
    print("Buzzer de-initialized.")