import time
import Jetson.GPIO as GPIO

# Physical 40-pin header numbers
HOUSE_PINS = {
    "Sim Run Pin": 7,
    "House 1": 12,
    "House 2": 15,
    "House 3": 35,
    "House 4": 38,
    "House 5": 40,
}

GPIO.setmode(GPIO.BOARD)

try:
    # Configure all five pins as outputs, initially LOW
    for pin in HOUSE_PINS.values():
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    print("5-house GPIO test started.")
    print("Press Ctrl+C to stop.\n")

    while True:
        for house, pin in HOUSE_PINS.items():

            print(f"{house} ON  - physical pin {pin}")
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(1)

            GPIO.output(pin, GPIO.LOW)
            print(f"{house} OFF\n")
            time.sleep(0.5)

except KeyboardInterrupt:
    print("\nTest stopped.")

finally:
    # Make sure everything is switched off
    for pin in HOUSE_PINS.values():
        GPIO.output(pin, GPIO.LOW)

    GPIO.cleanup()
    print("GPIO cleanup complete.")
