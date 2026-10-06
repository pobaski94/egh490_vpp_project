import time
import serial
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

        # -----------------------------
        # Jetson GPIO setup
        # -----------------------------
        GPIO.setmode(GPIO.BOARD)

        for pin in self.HOUSE_PINS.values():
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        GPIO.setup(
            self.TICK_PIN,
            GPIO.OUT,
            initial=GPIO.LOW
        )

        # -----------------------------
        # ESP32 USB serial connection
        # -----------------------------
        self.serial = serial.Serial(
            "/dev/ttyACM0",
            115200,
            timeout=0.1
        )

        # Allow USB serial connection to settle
        time.sleep(2)

        self.serial.reset_input_buffer()

        # -----------------------------
        # Hardware input states
        # -----------------------------
        self.network_support_active = False

    def read_inputs(self):

        external_inputs = {}

        while self.serial.in_waiting:

            message = (
                self.serial
                .readline()
                .decode()
                .strip()
            )

            if message == "BUTTON,NETWORK_SUPPORT,PRESSED":

                self.network_support_active = (
                    not self.network_support_active
                )

                print(
                    f"Network support event: "
                    f"{'ON' if self.network_support_active else 'OFF'}"
                )

        external_inputs["network_support_request"] = (
            self.network_support_active
        )

        if self.network_support_active:
            external_inputs["requested_support_kw"] = 28.0

        return external_inputs

    def cleanup(self):

        for pin in self.HOUSE_PINS.values():
            GPIO.output(pin, GPIO.LOW)

        GPIO.output(self.TICK_PIN, GPIO.LOW)

        GPIO.cleanup()

        if self.serial.is_open:
            self.serial.close()

    def tick_on(self):
        GPIO.output(self.TICK_PIN, GPIO.HIGH)

    def tick_off(self):
        GPIO.output(self.TICK_PIN, GPIO.LOW)

    def all_house_leds_off(self):

        for pin in self.HOUSE_PINS.values():
            GPIO.output(pin, GPIO.LOW)
    
    def update_outputs(self, result, house_states):
        """
        Update the outputs for the ESP32S3 for one simulation step
        """
        active_mode = result["VPP_mode"]

        if active_mode == "network_support":
            self.serial.write(b"LED,RED\n")

        else:
            self.serial.write(b"LED,OFF\n")

        # -------------------------------------------
        # HOUSE BATTERY INDICATORS
        # -------------------------------------------

        for house, state in house_states.items():

            house_number = int(house.split()[-1])

            command = (
                f"HOUSE,{house_number},{state.upper()}\n"
            )

            self.serial.write(command.encode())
            
            
            
        
    
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

                    output = GPIO.HIGH

                elif state == "charging":

                    output = (
                        GPIO.HIGH
                        if int(elapsed / 0.5) % 2 == 0
                        else GPIO.LOW
                    )

                elif state == "discharging":

                    output = (
                        GPIO.HIGH
                        if int(elapsed / 0.2) % 2 == 0
                        else GPIO.LOW
                    )

                else:

                    output = GPIO.LOW

                GPIO.output(pin, output)

            time.sleep(0.05)