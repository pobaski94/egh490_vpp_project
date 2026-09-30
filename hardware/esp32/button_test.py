import serial
import time

PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

with serial.Serial(PORT, BAUD_RATE, timeout=1) as esp32:

    # Allow USB serial connection to settle.
    time.sleep(2)

    esp32.reset_input_buffer()

    print("Listening for ESP32 button events...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            if esp32.in_waiting:
                message = esp32.readline().decode().strip()

                if message:
                    print(f"Received: {message}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nButton test stopped.")
