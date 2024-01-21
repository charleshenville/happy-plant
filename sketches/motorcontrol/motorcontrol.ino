/*
  The point of this micro controller is to get information from the backend API endppoint to:
  1. control the "watering arm" motor (motor is moved to angle 40 (or wtvr),
        when chasis controller sends a 1 to "stillAtPlantPin")

  2. control the motors (aka send digital binary info to other arduino)... move to the plant the API wants
      (convert plant select to binary and output to plantSelMSPin, and plantSelLSPin)
*/

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Servo.h>

const char *ssid = "charleshen";
const char *password = "thatiscool";

Servo Servo1;
// Your Domain name with URL path or IP address with path
//  Replace with your server details
const String serverName = "http://174.93.52.42:8080";
// const char* server = "samuraimain.ddns.net";
int port = 8080;

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastTime = 0;
// Timer set to 10 minutes (600000)
// unsigned long timerDelay = 600000;
// Set timer to 5 seconds (5000)
unsigned long timerDelay = 5000;

// chassis pins (plant select)
#define plantSelMSPin D1   // most significant
#define plantSelLSPin D0   // least significant
#define stillAtPlantPin D2 // 1 if currently stationed at a plant, 0 if not
#define motorPin D3        //

// Function prototypes
void splitStringToInts(String input, char delimiter, int &value1, int &value2, int &value3);
void intToBinary(int num, int &bit1, int &bit0);

void setup()
{
    Serial.begin(9600);
    Servo1.attach(motorPin);
    Servo1.write(0);

    WiFi.begin(ssid, password);
    Serial.println("Connecting...");
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.print("Connected to WiFi network with IP Address: ");
    Serial.println(WiFi.localIP());

    Serial.println("Timer set to 5 seconds (timerDelay variable), it will take 5 seconds before publishing the first reading.");

    // setting up pins
    pinMode(plantSelMSPin, OUTPUT);
    pinMode(plantSelLSPin, OUTPUT);
    pinMode(stillAtPlantPin, INPUT);
    // pinMode(motorPin, OUTPUT);
}

void loop()
{
    // Send an HTTP POST request depending on timerDelay
    if ((millis() - lastTime) > timerDelay)
    {
        // Check WiFi connection status
        if (WiFi.status() == WL_CONNECTED)
        {
            WiFiClient client;
            HTTPClient http;

            String serverPath = serverName + "/get_activation";

            // Your Domain name with URL path or IP address with path
            http.begin(client, serverPath);

            // If you need Node-RED/server authentication, insert user and password below
            // http.setAuthorization("REPLACE_WITH_SERVER_USERNAME", "REPLACE_WITH_SERVER_PASSWORD");

            // Send HTTP GET request
            int httpResponseCode = http.GET();

            //
            if (httpResponseCode > 0)
            {
                Serial.print("HTTP Response code: ");
                Serial.println(httpResponseCode);
                // print the message from the API
                String payload = http.getString();
                Serial.println(payload);

                // separate the values (plantSelect, pourTime1, pourTime2)
                int plantSelect;
                int pourTime1;
                int pourTime2;
                splitStringToInts(payload, ',', plantSelect, pourTime1, pourTime2);

                int plantSelMSbit; // most significant
                int plantSelLSbit; // least significant
                // convert plantSelect to binary
                intToBinary(plantSelect, plantSelMSbit, plantSelLSbit);

                // send plantSelect binary digital signals to chassis adafruit controller
                digitalWrite(plantSelMSPin, plantSelMSbit);
                digitalWrite(plantSelLSPin, plantSelLSbit);

                // if the robot is currently stopping for a plant, move arm to 40 degrees
                if(plantSelMSbit || plantSelLSbit){
                    while (!digitalRead(stillAtPlantPin))
                    {
                        Serial.println("Waiting for ready signal...");
                    }
                    if(plantSelLSbit){
                        Servo1.write(40);
                        delay(pourTime1*750);
                        Servo1.write(0);
                        delay(1000);
                    }
                    if(plantSelMSbit){
                        while (digitalRead(stillAtPlantPin)){}
                        while (!digitalRead(stillAtPlantPin))
                        {
                            Serial.println("Waiting for ready signal...");
                        }
                        Servo1.write(40);
                        delay(pourTime2*750);
                        Servo1.write(0);
                    }
                }
            }
            else
            {
                Serial.print("Error code: ");
                Serial.println(httpResponseCode);
            }
            // Free resources
            http.end();
        }
        else
        {
            Serial.println("WiFi Disconnected");
        }
        lastTime = millis();
    }
}

void intToBinary(int num, int &bit1, int &bit0)
{
    // Use bitwise AND to extract individual bits
    bit0 = num & 0x01;        // Least significant bit
    bit1 = (num >> 1) & 0x01; // Most significant bit
}

// parses the "a,b,c" string to store the corresponding values vars
void splitStringToInts(String input, char delimiter, int &value1, int &value2, int &value3)
{
    // Find the position of the first delimiter
    int delimiterIndex1 = input.indexOf(delimiter);

    // Check if the delimiter was found
    if (delimiterIndex1 != -1)
    {
        // Extract the substring before the first delimiter
        String part1 = input.substring(0, delimiterIndex1);

        // Convert the substring to an integer
        value1 = part1.toInt();

        // Find the position of the second delimiter
        int delimiterIndex2 = input.indexOf(delimiter, delimiterIndex1 + 1);

        // Check if the second delimiter was found
        if (delimiterIndex2 != -1)
        {
            // Extract the substring between the first and second delimiters
            String part2 = input.substring(delimiterIndex1 + 1, delimiterIndex2);

            // Convert the substring to an integer
            value2 = part2.toInt();

            // Extract the substring after the second delimiter
            String part3 = input.substring(delimiterIndex2 + 1);

            // Convert the substring to an integer
            value3 = part3.toInt();
        }
    }
}
