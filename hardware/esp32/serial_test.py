import serial
import time

PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

with serial.Serial(PORT, BAUD_RATE, timeout=2) as esp32:

    # Give the ESP32/USB connection time to settle.
    time.sleep(2)

    # Clear anything already waiting in the receive buffer.
    esp32.reset_input_buffer()

    print("Sending: PING")
    esp32.write(b"PING\n")

    response = esp32.readline().decode().strip()

    print(f"Received: {response}")
