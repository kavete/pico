from machine import ADC, Pin
import time

R_fixed = 470  # 68kΩ
Vcc = 5
ldr = ADC(Pin(27))

while True:
    ldr_raw = ldr.read_u16()
    vout = (ldr_raw / 65535) * Vcc

#     if vout >= 4.95:
#         lux = 700  # Max brightness
#         ldr_resistance = 0.01  # practically zero
#         print("Room is fully bright — Lux clamped to max value")
#     elif vout <= 0.05:
#         lux = 0.1  # Too dark, minimal lux
#         ldr_resistance = 1e6  # simulate very high resistance
#         print("Room is very dark — Lux clamped to min value")
#     else:
#         ldr_resistance = ((Vcc - vout) * R_fixed) / vout
    lux = vout * (1200/5)

#     print("LDR Resistance: {:.2f} Ω".format(ldr_resistance))
    print("Estimated Lux: {:.2f}".format(lux))
    print("Raw ADC Value: ", ldr_raw)
    print("Voltage (Vout): {:.2f} V".format(vout))

    time.sleep(1)
