#include "DHT.h"

DHT dht(3, DHT22);

void setup() {
  Serial.begin(9600);
  Serial.println("DHTxx test!");

  pinMode(2, INPUT);
  pinMode(13, OUTPUT);
    
  dht.begin();
}

void loop() {
  /* 360 is (2 sec interval between DHT polls)
            --------------------------------------
            strlen("PIR: 0\n") * 8 / (9600 bits/s)
   */
  for (int i = 0; i < 360; i++)
  {
    Serial.print("PIR: ");
    Serial.println(digitalRead(2));
    digitalWrite(13, digitalRead(2));
  }
  
  float h = dht.readHumidity();
  Serial.print("Humidity: ");
  Serial.println(h);  
  float t = dht.readTemperature();
  Serial.print("Temperature: ");
  Serial.println(t);
}
