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
int wet = 250;
int dry = 650;
double minsPerRequest = 0.1;

WiFiClient wifiClient;
HttpClient client = HttpClient(wifiClient, server, port);

int moistThresh = 5;

hp_BH1750 luxSensor;
int lux = 0;

const int motorPin = 3;

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
double cmap(int x, int in_min, int in_max, int out_min, int out_max) {
  double result = (static_cast<double>(x) - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
  return result;
}
void loop() {
  // Sample data to be sent
  int moisture_level = analogRead(A1);
  int moisture_level_2 = analogRead(A2);
  int moisture_level_3 = analogRead(A3);
  double percentageHumidity = min(max(0.0, cmap(moisture_level, wet, dry, 100.0, 0.0)), 100.0);
  double percentageHumidity_2 = min(max(0.0, cmap(moisture_level_2, wet, dry, 100.0, 0.0)), 100.0);
  double percentageHumidity_3 = min(max(0.0, cmap(moisture_level_3, wet, dry, 100.0, 0.0)), 100.0);

  luxSensor.start();
  float sunlight_level = luxSensor.getLux();

  // Creating payload
  String queryString ="?query=" + String(percentageHumidity) + "+" + String(percentageHumidity_2) + "+" + String(percentageHumidity_3) + "+" + String(sunlight_level);

  // Make a GET request w query arg
  Serial.println(queryString);
  client.beginRequest();
  client.get("/get_data" + queryString);
  client.endRequest();

  // Check the response
  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("HTTP Status Code: ");
  Serial.println(statusCode);
  Serial.print("Response: ");
  Serial.println(response);

  delay(minsPerRequest*60000);
}
