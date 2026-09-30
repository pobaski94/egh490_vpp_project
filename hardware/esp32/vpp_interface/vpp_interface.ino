#include <Arduino.h>

#define RGB_LED_PIN 21
#define BUTTON_PIN 1

bool lastRawButtonState = HIGH;
bool stableButtonState = HIGH;

unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;


String command = "";

void setLed(uint8_t red, uint8_t green, uint8_t blue) {
    rgbLedWrite(RGB_LED_PIN, red, green, blue);
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    
    setLed(0, 0, 0);

    Serial.println("READY");
}

void loop() {
    
bool rawButtonState = digitalRead(BUTTON_PIN);

    if (rawButtonState != lastRawButtonState) {
        lastDebounceTime = millis();
        lastRawButtonState = rawButtonState;
    }

    if ((millis() - lastDebounceTime) > debounceDelay) {

        if (rawButtonState != stableButtonState) {
            stableButtonState = rawButtonState;

            if (stableButtonState == LOW) {
                Serial.println("BUTTON,NETWORK_SUPPORT,PRESSED");
            }
        }
    }



    if (Serial.available()) {

        command = Serial.readStringUntil('\n');
        command.trim();

        if (command == "PING") {
            Serial.println("PONG");
        }

        else if (command == "LED,RED") {
            setLed(0, 255, 0);
            Serial.println("OK,LED,RED");
        }

        else if (command == "LED,GREEN") {
            setLed(255, 0, 0);
            Serial.println("OK,LED,GREEN");
        }

        else if (command == "LED,BLUE") {
            setLed(0, 0, 255);
            Serial.println("OK,LED,BLUE");
        }

        else if (command == "LED,OFF") {
            setLed(0, 0, 0);
            Serial.println("OK,LED,OFF");
        }

        else {
            Serial.print("ERROR,UNKNOWN_COMMAND,");
            Serial.println(command);
        }
    }
}
