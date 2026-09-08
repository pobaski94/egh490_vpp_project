from hardware_interface import HardwareInterface


hardware = HardwareInterface()

try:

    print("Hardware LED demonstration started.")
    print("Press Ctrl+C to stop.\n")

    test_states = [
        {
            "House 1": "full",
            "House 2": "charging",
            "House 3": "no_battery",
            "House 4": "discharging",
            "House 5": "minimum",
        },

        {
            "House 1": "discharging",
            "House 2": "full",
            "House 3": "no_battery",
            "House 4": "charging",
            "House 5": "charging",
        },
    ]

    step = 0

    while True:

        states = test_states[step % len(test_states)]

        print(f"Demo step {step}")

        for house, state in states.items():
            print(f"  {house}: {state}")

        hardware.display_states(
            house_states=states,
            duration=3.0
        )

        step += 1

except KeyboardInterrupt:
    print("\nDemo stopped.")

finally:
    hardware.cleanup()
