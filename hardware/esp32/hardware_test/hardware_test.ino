#include <Arduino.h>

#define RGB_LED_PIN 2

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("ESP32-S3-Zero started");

    // ESP32-S3-Zero onboard addressable RGB LED
    rgbLedWrite(RGB_LED_PIN, 0, 0, 0);
}

void loop() {
    // Green
    //Serial.println("CHANNEL 1");
    //rgbLedWrite(RGB_LED_PIN, 255, 0, 0);
    //delay(2000);

    // red
    //Serial.println("CHANNEL 2");
    //rgbLedWrite(RGB_LED_PIN, 0, 255, 0);
    //delay(2000);

    // Blue
    //Serial.println("CHANNEL 3");
    //rgbLedWrite(RGB_LED_PIN, 0, 0, 255);
    //delay(2000);

    // Full White
    Serial.println("FULL WHITE");
    rgbLedWrite(RGB_LED_PIN, 255, 255, 255);
    //delay(2000);

}

