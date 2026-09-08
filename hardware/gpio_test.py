import time
import Jetson.GPIO as GPIO

#this is pin 12 for the gpio pin led  test
LED_GPIO_PIN = 12

GPIO.setmode(GPIO.BOARD)

try:
    GPIO.setup(LED_GPIO_PIN, GPIO.OUT, initial=GPIO.LOW)

    print("GPIO test started. Press Ctrl+C to stop.")

    while True:
        GPIO.output(LED_GPIO_PIN, GPIO.HIGH)
        print("HIGH")
        time.sleep(1)

        GPIO.output(LED_GPIO_PIN, GPIO.LOW)
        print("LOW")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nGPIO test stopped.")

finally:
    GPIO.output(LED_GPIO_PIN, GPIO.LOW)
    GPIO.cleanup()
