#include <Arduino.h>

#define RGB_LED_PIN 21

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("ESP32-S3-Zero started");

    // ESP32-S3-Zero onboard addressable RGB LED
    rgbLedWrite(RGB_LED_PIN, 0, 0, 0);
}

void loop() {
    // Red
    Serial.println("RED");
    rgbLedWrite(RGB_LED_PIN, 255, 0, 0);
    delay(1000);

    // Green
    Serial.println("GREEN");
    rgbLedWrite(RGB_LED_PIN, 0, 255, 0);
    delay(1000);

    // Blue
    Serial.println("BLUE");
    rgbLedWrite(RGB_LED_PIN, 0, 0, 255);
    delay(1000);
}
