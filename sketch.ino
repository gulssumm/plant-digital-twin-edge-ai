#include "DHT.h"
#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

const int ldrPin = A0;
const int buttonPin = 4;

// Timing and Signal Variables
unsigned long lastDHTRead = 0;
float temp = 25.0;
float hum = 60.0;
int timer = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  // Activate the internal pull-up resistor for the button
  pinMode(buttonPin, INPUT_PULLUP);
  
  // Hardware Stabilization: Wait half a second for voltages to settle
  delay(500);
  
  // Clear any garbage data from the serial buffer during startup
  Serial.flush();
}

void loop() {
  // Asynchronous Reading: Read DHT sensor every 1 second without blocking the loop
  if (millis() - lastDHTRead > 1000) {
    temp = dht.readTemperature();
    hum = dht.readHumidity();
    lastDHTRead = millis();
  }

  // Read instantaneous data from Light Sensor and Button
  int lightLevel = analogRead(ldrPin);
  bool isTrauma = (digitalRead(buttonPin) == LOW); // LOW means the button is pressed

  // Baseline Wander: Simulates the plant's slow natural circadian rhythm or temperature drift
  // Instead of a flat 500, the baseline slowly breathes up and down.
  int baselineDrift = sin(timer * 0.02) * 50; 
  int ecgBaseline = 500 + baselineDrift;
  
  int ecgSignal = ecgBaseline;
  int stateLabel = 0; 

  // Physical Trauma 
  if (isTrauma) {
    stateLabel = 2;
    // Asymmetric, high-frequency shockwave combined with heavy random noise
    ecgSignal += sin(timer * 1.5) * 120 + random(-150, 350); 
  }
  // Environmental Stress
  else if (temp > 30.0 || hum < 40.0 || lightLevel > 800) { 
    stateLabel = 1;
    // Harmonic Overlap: Two different waves colliding creates a chaotic, unpredictable rhythm
    ecgSignal += sin(timer * 0.4) * 80 + cos(timer * 0.15) * 60 + random(-50, 40);
  }
  // Normal (Calm)
  else {
    stateLabel = 0;
    // Imperfect Peace: Two slow waves overlapping with slight natural vibration
    ecgSignal += sin(timer * 0.1) * 30 + sin(timer * 0.05) * 20 + random(-15, 15);
  }

  Serial.print(ecgSignal);
  Serial.print(",");
  Serial.println(stateLabel);

  timer++;
  delay(20); // Dictates the sampling rate (50Hz = 50 readings per second)
}