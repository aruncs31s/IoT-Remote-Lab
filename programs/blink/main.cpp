#include <Arduino.h>

void setup() {
  Serial.begin(9600);
  pinMode(LED,1);
}

void loop() {
  Serial.println("Hello, World!");
  // put your main code here, to run repeatedly:
}
