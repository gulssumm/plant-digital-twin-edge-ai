#include "DHT.h"
#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

const int ldrPin = A0;
const int buttonPin = 4;

unsigned long lastDHTRead = 0;
float temp = 25.0;
float hum = 60.0;
int timer = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  # reading DHT sensor every 1 second
  if (millis() - lastDHTRead > 1000) {
    temp = dht.readTemperature();
    hum = dht.readHumidity();
    lastDHTRead = millis();
  }

  int lightLevel = analogRead(ldrPin);
  bool isTrauma = (digitalRead(buttonPin) == LOW);  // if it is LOW it means the button is pressed

  int ecgBaseline = 500;
  int ecgSignal = ecgBaseline;
  int stateLabel = 0; // 0: Normal, 1: Stress, 2: Physical Trauma

 // Physical Trauma
  if (isTrauma) {
    stateLabel = 2;
    // A severe, high-amplitude Action Potential spike caused by a torn leaf
    ecgSignal += random(-300, 300); 
  }
  // Stress
  else if (temp > 30.0 || hum < 40.0 || lightLevel > 800) { 
    stateLabel = 1;
    // Stressed rhythm: Irregular, chaotic, and heavy fluctuations akin to a heartbeat
    ecgSignal += sin(timer * 0.4) * 120 + random(-30, 30);
  }
  // Normal
  else {
    stateLabel = 0;
    // Peaceful rhythm: A slow, highly regular, and gentle wave resembling a breathing pattern
    ecgSignal += sin(timer * 0.1) * 40 + random(-5, 5);
  }
  
  Serial.print(ecgSignal);
  Serial.print(",");
  Serial.println(stateLabel);

  timer++;
  delay(20); // 50 Hz sampling rate
}