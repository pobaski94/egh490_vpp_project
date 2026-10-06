#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

#define RGB_LED_PIN 21
#define HOUSE_LED_PIN 2
#define HOUSE_LED_COUNT 5
#define BUTTON_PIN 1

#define SOC_LED_PIN 13
#define SOC_LED_COUNT 20

// set up battery SOC LEDS
Adafruit_NeoPixel socLeds(
    SOC_LED_COUNT,
    SOC_LED_PIN,
    NEO_GRB + NEO_KHZ800
);

// set ip house battery status leds

Adafruit_NeoPixel houseLeds(
    HOUSE_LED_COUNT,
    HOUSE_LED_PIN,
    NEO_RGB + NEO_KHZ800
);

bool lastRawButtonState = HIGH;
bool stableButtonState = HIGH;

unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;


String command = "";

void setLed(uint8_t red, uint8_t green, uint8_t blue) {
    rgbLedWrite(RGB_LED_PIN, red, green, blue);
}


void setHouseState(int house, String state) {
    int pixel = house - 1;

    if (pixel < 0 || pixel >= HOUSE_LED_COUNT) {
        return;
    }

    if (state == "CHARGING") {
        houseLeds.setPixelColor(pixel, houseLeds.Color(0,0,50));
    }

    else if (state == "DISCHARGING") {
        houseLeds.setPixelColor(pixel, houseLeds.Color(50,0,0));
    }

    else if (state == "FULL") {
        houseLeds.setPixelColor(pixel, houseLeds.Color(0,50,0));
    }
    
    else {
        houseLeds.setPixelColor(pixel, houseLeds.Color(0,0,0));
    }

    houseLeds.show();
}

void setSocBar(int house, int socPercent) {

    int ledsOn = 0;
    int startPixel = (house - 1) * 4;
    
    if (socPercent <=0) {
        ledsOn = 0;
    }

    else if (socPercent <= 25) {
        ledsOn = 1;
    }
        
    else if (socPercent <= 50) {
        ledsOn = 2;
    }
    else if (socPercent <= 75) {
        ledsOn = 3;
    }
    else {
        ledsOn = 4;
    }

    for (int j = 0; j < 4; j++) {
        socLeds.setPixelColor(
            startPixel + j,
            socLeds.Color(0,0,0)
            );
    }

    for (int i = 0; i < ledsOn; i++) {
        socLeds.setPixelColor(
            startPixel + i,
            socLeds.Color(100, 100, 100)
        );
    }

    socLeds.show();
}




void setup() {
    Serial.begin(115200);
    delay(1000);
    
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    houseLeds.begin();
    houseLeds.clear();
    houseLeds.show();
    setLed(0, 0, 0);
    socLeds.begin();
    socLeds.clear();
    socLeds.show();

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

        else if (command == "HOUSE,TEST") {
        
            houseLeds.clear();
        
            houseLeds.setPixelColor(0, houseLeds.Color(255, 0, 0));
            houseLeds.setPixelColor(1, houseLeds.Color(0, 255, 0));
            houseLeds.setPixelColor(2, houseLeds.Color(0, 0, 255));
            houseLeds.setPixelColor(3, houseLeds.Color(255, 255, 255));
            houseLeds.setPixelColor(4, houseLeds.Color(0, 0, 0));
        
            houseLeds.show();
        
            Serial.println("OK,HOUSE,TEST");
        }

        else if (command.startsWith("HOUSE,")) {
            int firstComma = command.indexOf(',');
            int secondComma = command.indexOf(',', firstComma + 1);

            int house = command.substring(
                firstComma + 1,
                secondComma
            ).toInt();

            String state = command.substring(secondComma +1);

            setHouseState(house, state);

            Serial.print("OK,HOUSE,");
            Serial.print(house);
            Serial.print(",");
            Serial.println(state);
        }


        else if (command == "SOC,TEST") {
            

            socLeds.clear();
            socLeds.setPixelColor(0, socLeds.Color(255,0,0));
            socLeds.setPixelColor(1, socLeds.Color(0,255,0));
            socLeds.setPixelColor(2, socLeds.Color(0,0,255));
            socLeds.setPixelColor(3, socLeds.Color(255,255,255));

            socLeds.show();

            Serial.println("OK,SOC,TEST");
        }

        else if (command.startsWith("SOC,1,")) {
            
            
            int secondComma = command.indexOf(',', 4);

            int socPercent = command.substring(
                secondComma + 1
            ).toInt();
        
            setSocBar(1, socPercent);
        
            Serial.print("OK,SOC,1,");
            Serial.println(socPercent);
        }
        else if (command.startsWith("SOC,2,")) {
            
            
            int secondComma = command.indexOf(',', 4);

            int socPercent = command.substring(
                secondComma + 1
            ).toInt();
        
            setSocBar(2, socPercent);
        
            Serial.print("OK,SOC,2,");
            Serial.println(socPercent);
        }
        else if (command.startsWith("SOC,3,")) {
            
            
            int secondComma = command.indexOf(',', 4);

            int socPercent = command.substring(
                secondComma + 1
            ).toInt();
        
            setSocBar(3, socPercent);
        
            Serial.print("OK,SOC,3,");
            Serial.println(socPercent);
        }
            
        else if (command.startsWith("SOC,4,")) {
            
            
            int secondComma = command.indexOf(',', 4);

            int socPercent = command.substring(
                secondComma + 1
            ).toInt();
        
            setSocBar(4, socPercent);
        
            Serial.print("OK,SOC,4,");
            Serial.println(socPercent);
        }
            
        else if (command.startsWith("SOC,5,")) {
            
            
            int secondComma = command.indexOf(',', 4);

            int socPercent = command.substring(
                secondComma + 1
            ).toInt();
        
            setSocBar(5, socPercent);
        
            Serial.print("OK,SOC,5,");
            Serial.println(5, socPercent);
        }

        else if (command == "LEDS,OFF") {
            
            socLeds.clear();
            houseLeds.clear();
            socLeds.show();
            houseLeds.show();
            setLed(0,0,0);
                        
    
            Serial.println("OK,LEDS,OFF");
        
        }

        
        else {
            Serial.print("ERROR,UNKNOWN_COMMAND,");
            Serial.println(command);
        }
    }
}
