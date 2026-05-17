#include "DHT.h"

// Sensör Pin Ayarları
#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

const int ldrPin = A0;
const int buttonPin = 4;

// Zamanlama ve Sinyal Değişkenleri
unsigned long lastDHTRead = 0;
float temp = 25.0;
float hum = 60.0;
int timer = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  // Buton için dahili pull-up direncini aktifleştir
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  // DHT22 okuma işlemi yavaştır (yaklaşık 250ms sürer). 
  // Sinyal akışımızın takılmaması için sıcaklığı sadece saniyede 1 kez okuyoruz.
  if (millis() - lastDHTRead > 1000) {
    temp = dht.readTemperature();
    hum = dht.readHumidity();
    lastDHTRead = millis();
  }

  // Işık ve Buton (Travma) verilerini anlık oku
  int lightLevel = analogRead(ldrPin);
  bool isTrauma = (digitalRead(buttonPin) == LOW); // LOW ise butona basılmıştır

  // Biyolojik Sinyal Üretimi
  int ecgBaseline = 500;
  int ecgSignal = ecgBaseline;
  int stateLabel = 0; // 0: Normal, 1: Çevresel Stres, 2: Fiziksel Travma

  // DURUM 2: Akut Fiziksel Travma (Öncelikli durum)
  if (isTrauma) {
    stateLabel = 2;
    // Bir yaprak koptuğunda oluşan şiddetli, yüksek genlikli Action Potential çığlığı
    ecgSignal += random(-300, 300); 
  }
  // DURUM 1: Çevresel Stres (Sıcaklık 30'dan büyük, nem %40'tan küçük veya çok karanlık)
  else if (temp > 30.0 || hum < 40.0 || lightLevel > 800) { 
    stateLabel = 1;
    // Stresli ritim: Kalp atışı gibi düzensiz, kaotik ve ağır bir dalgalanma
    ecgSignal += sin(timer * 0.4) * 120 + random(-30, 30);
  }
  // DURUM 0: Normal (Huzurlu Bitki)
  else {
    stateLabel = 0;
    // Huzurlu ritim: Nefes alır gibi yavaş, çok düzenli ve yumuşak bir dalga
    ecgSignal += sin(timer * 0.1) * 40 + random(-5, 5);
  }

  // Veriyi Python'ın makine öğrenmesi modeline uygun formatta gönder: "Sinyal,Durum"
  Serial.print(ecgSignal);
  Serial.print(",");
  Serial.println(stateLabel);

  timer++;
  delay(20); // Grafiğin akış hızını belirler (Saniyede ~50 veri)
}