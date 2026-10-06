import time
import serial
import Jetson.GPIO as GPIO


class HardwareInterface:

    def __init__(self):
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

        if self.serial.is_open:
            self.serial.write(b"LEDS,OFF\n")
            self.serial.close()


    
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

        for house, data in house_states.items():

            house_number = int(house.split()[-1])

            state = data["state"]
            soc_percent = data["soc_percent"]
            
            # Send battery operating state
            
            command = (
                f"HOUSE,{house_number},{state.upper()}\n"
            )

            self.serial.write(command.encode())

            # Send battery SOC
            command = (
                f"SOC,{house_number},{round(soc_percent)}\n"
            )
            
            self.serial.write(command.encode())
            
            
