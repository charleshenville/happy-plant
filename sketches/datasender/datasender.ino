#include "WiFiS3.h"
#include <hp_BH1750.h>
#include <ArduinoHttpClient.h>
#include <Servo.h>

const char* ssid = "charleshen";
const char* pass = "thatiscool";

Servo Servo1;

const char* server = "174.93.52.42";
// const char* server = "samuraimain.ddns.net";
int port = 8080;
int wet = 200;
int dry = 620;

WiFiClient wifiClient;
HttpClient client = HttpClient(wifiClient, server, port);

hp_BH1750 luxSensor;
int lux = 0;

const int motorpin = 3;

void setup() {
  Serial.begin(9600);
  delay(2000);

  Servo1.attach(motorPin);
  Servo1.write(40);

  bool avail = luxSensor.begin(BH1750_TO_GROUND);
  // Connect to WiFi
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.println("Connecting to WiFi...");
    delay(1000);
  }

  Serial.println("Connected to WiFi");
}

void loop() {
  // Sample data to be sent
  float moisture_level = analogRead(A1);
  float moisture_level_2 = analogRead(A2);
  float percentageHumididy = map(moisture_level, wet, dry, 100, 0);
  float percentageHumididy_2 = map(moisture_level_2, wet, dry, 100, 0);

  if(percentageHumididy < 30.0 || percentageHumididy_2 < 30.0){
    Servo1.write(180);
    float hm = percentageHumididy<percentageHumididy_2?percentageHumididy:percentageHumididy_2;
    delay((int)((30.0-hm)*1000))
    Servo1.write(40);
  }
  luxSensor.start();
  float sunlight_level = luxSensor.getLux();

  // Creating payload
  String queryString ="?query=" + String(percentageHumididy) + "+" + String(percentageHumididy_2) + "+" + String(sunlight_level);

  // Make a GET request w query arg
  Serial.println(queryString);
  client.beginRequest();
  client.get("/get_data" + queryString); // Replace with your API endpoint
  // client.sendHeader("Host", server);
  // client.sendHeader("Connection", "close");
  client.endRequest();

  // Check the response
  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("HTTP Status Code: ");
  Serial.println(statusCode);
  Serial.print("Response: ");
  Serial.println(response);

  delay(2000); // Send request every 10 seconds
}
