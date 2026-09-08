import time
import Jetson.GPIO as GPIO


class HardwareInterface:

    HOUSE_PINS = {
        "House 1": 12,
        "House 2": 15,
        "House 3": 35,
        "House 4": 38,
        "House 5": 40,
    }

    TICK_PIN = 7

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

        for pin in self.HOUSE_PINS.values():
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        GPIO.setup(self.TICK_PIN, GPIO.OUT, initial=GPIO.LOW)

    def cleanup(self):
        for pin in self.HOUSE_PINS.values():
            GPIO.output(pin, GPIO.LOW)

        GPIO.output(self.TICK_PIN, GPIO.LOW)
        GPIO.cleanup()

    def tick_on(self):
        GPIO.output(self.TICK_PIN, GPIO.HIGH)

    def tick_off(self):
        GPIO.output(self.TICK_PIN, GPIO.LOW)

    def all_house_leds_off(self):
        for pin in self.HOUSE_PINS.values():
            GPIO.output(pin, GPIO.LOW)

    def display_states(self, house_states, duration=3.0):
        """
        Display house battery states for one simulation timestep.
        """

        start_time = time.time()

        # Brief flash to indicate a new timestep
        self.tick_on()
        time.sleep(0.15)
        self.tick_off()

        while time.time() - start_time < duration:

            elapsed = time.time() - start_time

            for house, state in house_states.items():
                pin = self.HOUSE_PINS[house]

                if state == "full":
                    # solid on
                    output = GPIO.HIGH

                elif state == "charging":
                    # Slow flash
                    output = (
                        GPIO.HIGH
                        if int(elapsed / 0.5) % 2 == 0
                        else GPIO.LOW
                    )

                elif state == "discharging":
                    # Fast flash
                    output = (
                        GPIO.HIGH
                        if int(elapsed / 0.2) % 2 == 0
                        else GPIO.LOW
                    )

                else:
                    # idle, minimum SOC, no battery, etc.
                    output = GPIO.LOW

                GPIO.output(pin, output)

            time.sleep(0.05)
