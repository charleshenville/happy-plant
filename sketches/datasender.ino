#include "WiFiS3.h"
#include <ArduinoHttpClient.h>

// Replace with your WiFi credentials
const char* ssid = "charleshen";
const char* pass = "thatiscool";

// Replace with your server details
const char* server = "174.93.52.42";
// const char* server = "samuraimain.ddns.net";

int port = 8080;

WiFiClient wifiClient;
HttpClient client = HttpClient(wifiClient, server, port);

void setup() {
  Serial.begin(9600);
  delay(2000);

  // Connect to WiFi
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.println("Connecting to WiFi...");
    delay(1000);
  }

  Serial.println("Connected to WiFi");
}

void loop() {
  // Sample data to be sent
  int moisture_level = analogRead(A0);
  // int sunlight_level = analogRead(A1);

  //int moisture_level = 10;
  int sunlight_level = 10;

  // Create JSON payload
  String queryString ="?query="+String(moisture_level) + "+" + String(sunlight_level);

  // Make a POST request
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
